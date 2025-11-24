import React, { useState, useEffect } from "react";

// Kiosk Nutrition Planner - Single-file React component
// - Tailwind CSS assumed available in the hosting environment
// - Uses localStorage for saved profiles
// - Basic food DB included for demo; in production, swap with server DB

export default function KioskNutritionApp() {
  // --- User inputs ---
  const [age, setAge] = useState(30);
  const [sex, setSex] = useState("male");
  const [height, setHeight] = useState(175);
  const [weight, setWeight] = useState(70);
  const [activity, setActivity] = useState("moderate"); // sedentary, light, moderate, active
  const [goal, setGoal] = useState("maintain"); // lose, maintain, gain
  const [mealsPerDay, setMealsPerDay] = useState(3);
  const [allergies, setAllergies] = useState([]);
  const [dietType, setDietType] = useState("omnivore");
  const [cooking, setCooking] = useState("home");
  const [budgetLevel, setBudgetLevel] = useState("medium");

  // --- Computed targets ---
  const [bmr, setBmr] = useState(0);
  const [tdee, setTdee] = useState(0);
  const [kcalTarget, setKcalTarget] = useState(2000);
  const [macroTargets, setMacroTargets] = useState({ protein_g: 70, carbs_g: 250, fat_g: 70 });
  const [fiberTarget, setFiberTarget] = useState(25);
  const [sodiumLimit, setSodiumLimit] = useState(2300);

  // --- Generated plan ---
  const [plan, setPlan] = useState([]);
  const [foodDB, setFoodDB] = useState(INITIAL_FOOD_DB);

  // --- UI state ---
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [profileName, setProfileName] = useState("");

  useEffect(() => {
    calculateTargets();
  }, [age, sex, height, weight, activity, goal]);

  useEffect(() => {
    // regenerate quick plan when targets change
    generatePlan();
  }, [kcalTarget, macroTargets, fiberTarget, sodiumLimit, foodDB]);

  // --- Calculation helpers ---
  function calcBMR({ sex, weight, height, age }) {
    // Mifflin-St Jeor
    if (sex === "male") {
      return 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      return 10 * weight + 6.25 * height - 5 * age - 161;
    }
  }

  function activityFactor(level) {
    switch (level) {
      case "sedentary":
        return 1.2;
      case "light":
        return 1.375;
      case "moderate":
        return 1.55;
      case "active":
        return 1.725;
      default:
        return 1.55;
    }
  }

  function calculateTargets() {
    const b = calcBMR({ sex, weight, height, age });
    setBmr(Math.round(b));
    const t = Math.round(b * activityFactor(activity));
    setTdee(t);

    // goal adjustments
    let kcal = t;
    if (goal === "lose") kcal = Math.max(1200, t - 500);
    if (goal === "gain") kcal = t + 300;
    setKcalTarget(kcal);

    // macros: default distribution carb 50%, protein based on weight, fat rest
    const protein_g = Math.round((goal === "gain" ? 1.4 : goal === "lose" ? 1.2 : 1.1) * weight);
    const protein_kcal = protein_g * 4;
    const carbs_kcal = Math.round(kcal * 0.5);
    const carbs_g = Math.round(carbs_kcal / 4);
    const fat_kcal = kcal - (protein_kcal + carbs_kcal);
    const fat_g = Math.round(fat_kcal / 9);

    setMacroTargets({ protein_g, carbs_g, fat_g });

    // fiber target: 14 g per 1000 kcal
    setFiberTarget(Math.round((kcal / 1000) * 14));
  }

  // --- Simple planner ---
  // Greedy meal assembling by matching protein first then carbs and fats
  function generatePlan() {
    // Build filtered food list by allergies/diet
    const avail = foodDB.filter((f) => {
      if (allergies.some((a) => f.allergens?.includes(a))) return false;
      if (dietType === "vegetarian" && f.type === "meat") return false;
      if (dietType === "vegan" && f.type !== "plant") return false;
      return true;
    });

    // Distribute kcal per meal: simple heuristic
    const mealDistribution = getMealDistribution(mealsPerDay);
    const mealPlans = mealDistribution.map((share, idx) => {
      const targetKcal = Math.round(kcalTarget * share);
      const slot = assembleMeal(avail, targetKcal, macroTargets, idx);
      return slot;
    });

    setPlan(mealPlans);
  }

  function getMealDistribution(n) {
    // default 3 meals + snack -> [0.25,0.35,0.30,0.10]
    if (n === 2) return [0.55, 0.45];
    if (n === 3) return [0.25, 0.4, 0.35];
    if (n === 4) return [0.22, 0.33, 0.3, 0.15];
    return Array(n).fill(1 / n);
  }

  function assembleMeal(availFoods, targetKcal, macros, mealIdx) {
    // greedy: pick a protein-rich item, then fill with carb item, add veg
    const meal = { items: [], kcal: 0, protein_g: 0, carbs_g: 0, fat_g: 0, fiber_g: 0, sodium_mg: 0 };

    // 1) pick best protein candidate
    const proteins = availFoods
      .filter((f) => f.protein_g > 8)
      .sort((a, b) => b.protein_g - a.protein_g);
    if (proteins.length) {
      const p = proteins[mealIdx % proteins.length];
      addFoodToMeal(meal, p, 1);
    }

    // 2) add carb source
    const carbs = availFoods
      .filter((f) => f.carbs_g > 15)
      .sort((a, b) => b.carbs_g - a.carbs_g);
    if (carbs.length && meal.kcal < targetKcal) {
      const c = carbs[(mealIdx + 1) % carbs.length];
      addFoodToMeal(meal, c, 1);
    }

    // 3) add veg/fruit for fiber and micronutrients
    const vegs = availFoods.filter((f) => f.type === "veg" || f.type === "fruit").slice(0, 2);
    vegs.forEach((v) => addFoodToMeal(meal, v, 1));

    // 4) small nuts or dairy for fats
    const fats = availFoods.filter((f) => f.fat_g >= 5).slice(0, 1);
    fats.forEach((f) => addFoodToMeal(meal, f, 1));

    // 5) if kcal short, add extra carb portion
    while (meal.kcal < targetKcal - 80) {
      const filler = carbs[0] || availFoods[0];
      if (!filler) break;
      addFoodToMeal(meal, filler, 0.5);
      if (meal.items.length > 8) break;
    }

    return meal;
  }

  function addFoodToMeal(meal, food, portions = 1) {
    const mult = portions;
    meal.items.push({ ...food, portions: mult });
    meal.kcal += Math.round((food.kcal || 0) * mult);
    meal.protein_g += Math.round((food.protein_g || 0) * mult);
    meal.carbs_g += Math.round((food.carbs_g || 0) * mult);
    meal.fat_g += Math.round((food.fat_g || 0) * mult);
    meal.fiber_g += Math.round((food.fiber_g || 0) * mult);
    meal.sodium_mg += Math.round((food.sodium_mg || 0) * mult);
  }

  // --- Profile save/load ---
  function saveProfile() {
    const profiles = JSON.parse(localStorage.getItem("kiosk_profiles") || "[]");
    const p = {
      name: profileName || `user_${Date.now()}`,
      age,
      sex,
      height,
      weight,
      activity,
      goal,
      mealsPerDay,
      allergies,
      dietType,
      cooking,
      budgetLevel,
      createdAt: new Date().toISOString(),
    };
    profiles.push(p);
    localStorage.setItem("kiosk_profiles", JSON.stringify(profiles));
    alert("프로필이 저장되었습니다.");
  }

  function loadProfiles() {
    const profiles = JSON.parse(localStorage.getItem("kiosk_profiles") || "[]");
    return profiles;
  }

  // --- Utility: export plan as QR/data URL (simple JSON) ---
  function exportPlanAsQR() {
    const payload = { kcalTarget, macroTargets, plan, date: new Date().toISOString() };
    const json = encodeURIComponent(JSON.stringify(payload));
    // For demo, create a data URL linking to a JSON blob. In production, replace with QR library.
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "meal_plan.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  // --- Food DB editor (simple) ---
  function addDemoFood() {
    const sample = {
      id: Date.now(),
      name: "두부(150g)",
      serving: "150g",
      kcal: 150,
      protein_g: 18,
      carbs_g: 4,
      fat_g: 8,
      fiber_g: 2,
      sodium_mg: 10,
      type: "plant",
      allergens: ["soy"],
    };
    setFoodDB((s) => [sample, ...s]);
  }

  // --- Rendering helpers ---
  function renderMealCard(meal, idx) {
    return (
      <div key={idx} className="p-4 border rounded-lg shadow-sm bg-white">
        <h4 className="font-semibold">{mealsPerDay === 2 && idx === 0 ? "아침/점심" : `끼니 ${idx + 1}`} </h4>
        <div className="text-sm text-gray-600">칼로리: {meal.kcal} kcal · 단백질: {meal.protein_g} g · 탄수: {meal.carbs_g} g · 지방: {meal.fat_g} g</div>
        <ul className="mt-2 space-y-1">
          {meal.items.map((it, i) => (
            <li key={i} className="flex items-center justify-between">
              <div>
                <div className="text-sm">{it.name} {it.portions !== 1 ? `×${it.portions}` : ""}</div>
                <div className="text-xs text-gray-500">서빙: {it.serving || "-"}</div>
              </div>
              <div className="text-xs text-gray-500">{it.kcal} kcal</div>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  // --- Main JSX ---
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white p-6">
      <div className="max-w-6xl mx-auto">
        <header className="mb-6">
          <h1 className="text-2xl font-bold">영양식 키오스크 - 맞춤 식단 설계</h1>
          <p className="text-sm text-gray-600">기본 정보를 입력하면 하루 권장 섭취량에 맞춘 1일 식단을 제안합니다.</p>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left: form */}
          <section className="col-span-1 p-4 bg-white rounded-lg shadow">
            <h2 className="font-semibold mb-3">기본 정보</h2>
            <div className="space-y-2 text-sm">
              <div className="flex gap-2">
                <label className="w-24">나이</label>
                <input type="number" className="flex-1 p-2 border rounded" value={age} onChange={(e) => setAge(Number(e.target.value))} />
              </div>
              <div className="flex gap-2">
                <label className="w-24">성별</label>
                <select value={sex} onChange={(e) => setSex(e.target.value)} className="flex-1 p-2 border rounded">
                  <option value="male">남성</option>
                  <option value="female">여성</option>
                </select>
              </div>
              <div className="flex gap-2">
                <label className="w-24">키(cm)</label>
                <input type="number" value={height} onChange={(e) => setHeight(Number(e.target.value))} className="flex-1 p-2 border rounded" />
              </div>
              <div className="flex gap-2">
                <label className="w-24">체중(kg)</label>
                <input type="number" value={weight} onChange={(e) => setWeight(Number(e.target.value))} className="flex-1 p-2 border rounded" />
              </div>

              <div className="flex gap-2">
                <label className="w-24">활동량</label>
                <select value={activity} onChange={(e) => setActivity(e.target.value)} className="flex-1 p-2 border rounded">
                  <option value="sedentary">거의 운동하지 않음</option>
                  <option value="light">가벼운 활동</option>
                  <option value="moderate">보통</option>
                  <option value="active">활발</option>
                </select>
              </div>

              <div className="flex gap-2">
                <label className="w-24">목표</label>
                <select value={goal} onChange={(e) => setGoal(e.target.value)} className="flex-1 p-2 border rounded">
                  <option value="maintain">유지</option>
                  <option value="lose">감량</option>
                  <option value="gain">증량(근육)</option>
                </select>
              </div>

              <div className="flex gap-2">
                <label className="w-24">끼니수</label>
                <select value={mealsPerDay} onChange={(e) => setMealsPerDay(Number(e.target.value))} className="flex-1 p-2 border rounded">
                  <option value={2}>2</option>
                  <option value={3}>3</option>
                  <option value={4}>4</option>
                </select>
              </div>

              <div className="flex gap-2 items-start">
                <label className="w-24">알레르기</label>
                <div className="flex-1 space-y-1 text-xs">
                  <label className="inline-flex items-center"><input type="checkbox" onChange={(e) => toggleAllergy("milk", e.target.checked)} /> 우유</label>
                  <label className="inline-flex items-center"><input type="checkbox" onChange={(e) => toggleAllergy("egg", e.target.checked)} /> 난류</label>
                  <label className="inline-flex items-center"><input type="checkbox" onChange={(e) => toggleAllergy("nuts", e.target.checked)} /> 견과류</label>
                  <label className="inline-flex items-center"><input type="checkbox" onChange={(e) => toggleAllergy("soy", e.target.checked)} /> 콩/대두</label>
                </div>
              </div>

              <div className="flex gap-2">
                <label className="w-24">식단 타입</label>
                <select value={dietType} onChange={(e) => setDietType(e.target.value)} className="flex-1 p-2 border rounded">
                  <option value="omnivore">일반(잡식)</option>
                  <option value="vegetarian">채식(락토/오보 가능)</option>
                  <option value="vegan">비건</option>
                </select>
              </div>

              <div className="pt-2 flex gap-2">
                <input type="text" placeholder="프로필 이름(선택)" value={profileName} onChange={(e) => setProfileName(e.target.value)} className="flex-1 p-2 border rounded" />
                <button onClick={saveProfile} className="px-3 py-2 bg-blue-600 text-white rounded">저장</button>
              </div>

              <div className="pt-2 flex gap-2">
                <button onClick={calculateTargets} className="flex-1 p-2 border rounded">목표 재계산</button>
                <button onClick={generatePlan} className="flex-1 p-2 border rounded">식단 재생성</button>
              </div>

              <div className="pt-2 text-xs text-gray-600">
                <button onClick={() => setShowAdvanced((s) => !s)} className="underline">고급 옵션 {showAdvanced ? "접기" : "펼치기"}</button>
              </div>

              {showAdvanced && (
                <div className="mt-2 text-xs space-y-2">
                  <div className="flex gap-2"><label className="w-24">예산</label>
                    <select value={budgetLevel} onChange={(e) => setBudgetLevel(e.target.value)} className="flex-1 p-2 border rounded">
                      <option value="low">저예산</option>
                      <option value="medium">중간</option>
                      <option value="high">여유</option>
                    </select>
                  </div>
                  <div className="flex gap-2"><label className="w-24">조리</label>
                    <select value={cooking} onChange={(e) => setCooking(e.target.value)} className="flex-1 p-2 border rounded">
                      <option value="home">직접 조리</option>
                      <option value="microwave">전자레인지 전용</option>
                      <option value="takeout">배달/테이크아웃</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Middle: targets & plan */}
          <section className="col-span-1 md:col-span-2 p-4 bg-white rounded-lg shadow space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="font-semibold">오늘의 영양 목표</h2>
                <div className="text-sm text-gray-600">BMR: {bmr} kcal · TDEE: {tdee} kcal</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold">{kcalTarget} kcal / 일</div>
                <div className="text-sm text-gray-600">단백질 {macroTargets.protein_g}g · 탄수 {macroTargets.carbs_g}g · 지방 {macroTargets.fat_g}g · 설유 {fiberTarget}g</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h3 className="font-medium">추천 식단 (끼니별)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {plan.length ? plan.map((m, i) => renderMealCard(m, i)) : <div className="p-4 border rounded">설정에 맞는 식단을 생성하세요.</div>}
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-medium">도움 기능</h3>
                <div className="p-3 border rounded">
                  <div className="flex gap-2">
                    <button className="flex-1 p-2 bg-green-600 text-white rounded" onClick={exportPlanAsQR}>식단 내보내기(JSON)</button>
                    <button className="flex-1 p-2 border rounded" onClick={addDemoFood}>DB에 샘플 추가</button>
                  </div>
                  <div className="mt-3 text-xs text-gray-600">
                    알레르기·종교 필터가 적용됩니다. 특정 재료를 누르면 대체 옵션을 보여줍니다.
                  </div>
                </div>

                <div className="p-3 border rounded">
                  <h4 className="font-semibold">레시피 및 조리</h4>
                  <div className="text-sm text-gray-600">각 끼니 카드에서 '레시피 보기'를 누르면 조리시간과 난이도를 제공합니다. 전자레인지 전용 옵션을 선택하면 간단 조리법으로 대체됩니다.</div>
                </div>

              </div>
            </div>

          </section>
        </main>

        <footer className="mt-6 text-sm text-gray-500 text-center">데모용 앱 — 상용 서비스 개발시 KDRIs(한국인 영양섭취기준)와 보건당국 권고를 반드시 참조하세요.</footer>
      </div>
    </div>
  );

  // --- small helper functions defined after JSX to keep above flow readable ---
  function toggleAllergy(name, checked) {
    setAllergies((s) => {
      const set = new Set(s);
      if (checked) set.add(name);
      else set.delete(name);
      return Array.from(set);
    });
  }
}

// --- Demo food DB ---
const INITIAL_FOOD_DB = [
  { id: 1, name: "닭가슴살(구이) 100g", serving: "100g", kcal: 165, protein_g: 31, carbs_g: 0, fat_g: 3.6, fiber_g: 0, sodium_mg: 60, type: "meat", allergens: [] },
  { id: 2, name: "현미밥 150g", serving: "150g", kcal: 210, protein_g: 4.4, carbs_g: 45, fat_g: 1.8, fiber_g: 2.8, sodium_mg: 5, type: "grain", allergens: [] },
  { id: 3, name: "연어(구이) 100g", serving: "100g", kcal: 208, protein_g: 20, carbs_g: 0, fat_g: 13, fiber_g: 0, sodium_mg: 50, type: "meat", allergens: ["fish"] },
  { id: 4, name: "두부 150g", serving: "150g", kcal: 144, protein_g: 17, carbs_g: 3.8, fat_g: 8.5, fiber_g: 1.2, sodium_mg: 12, type: "plant", allergens: ["soy"] },
  { id: 5, name: "오트밀(건조) 60g", serving: "60g", kcal: 230, protein_g: 8, carbs_g: 39, fat_g: 4, fiber_g: 6, sodium_mg: 2, type: "grain", allergens: ["gluten"] },
  { id: 6, name: "바나나(중) 1개", serving: "1개", kcal: 105, protein_g: 1.3, carbs_g: 27, fat_g: 0.3, fiber_g: 3.1, sodium_mg: 1, type: "fruit", allergens: [] },
  { id: 7, name: "그릭 요거트 150g", serving: "150g", kcal: 120, protein_g: 12, carbs_g: 8, fat_g: 4, fiber_g: 0, sodium_mg: 55, type: "dairy", allergens: ["milk"] },
  { id: 8, name: "혼합 견과류 20g", serving: "20g", kcal: 120, protein_g: 3, carbs_g: 4, fat_g: 10, fiber_g: 2, sodium_mg: 0, type: "nuts", allergens: ["nuts"] },
  { id: 9, name: "브로콜리(찜) 100g", serving: "100g", kcal: 35, protein_g: 2.8, carbs_g: 7, fat_g: 0.4, fiber_g: 3, sodium_mg: 30, type: "veg", allergens: [] },
  { id: 10, name: "고구마(중) 150g", serving: "150g", kcal: 130, protein_g: 2, carbs_g: 31, fat_g: 0.2, fiber_g: 3.8, sodium_mg: 36, type: "grain", allergens: [] },
];
