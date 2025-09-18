
from flask import Flask, request, jsonify, render_template
import json
import re
import logging
from datetime import datetime
import base64
import io

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# COMPREHENSIVE MEDICAL KNOWLEDGE BASE - Built from scratch for hackathon
MEDICAL_KNOWLEDGE_DATABASE = {
    # COMPLETE BLOOD COUNT (CBC)
    "hemoglobin": {
        "displayName": "Hemoglobin (Blood Oxygen Carrier)",
        "unit": "g/dL",
        "aliases": ["hgb", "hb", "hemoglobin level", "haemoglobin", "blood count"],
        "ranges": {"default": [12.0, 18.0], "male": [14.0, 18.0], "female": [12.0, 16.0]},
        "category": "blood_health",
        "organ_systems": ["cardiovascular", "respiratory", "blood"],
        "simple_explanation": {
            "what_it_is": "Hemoglobin is like tiny delivery trucks in your blood that carry oxygen from your lungs to every part of your body.",
            "why_important": "Without enough hemoglobin, your body doesn't get enough oxygen, making you feel tired and weak."
        },
        "interpretation": {
            "low": "Your hemoglobin is low, which means you might have anemia. This makes you feel tired because your body isn't getting enough oxygen.",
            "high": "Your hemoglobin is higher than normal. This could be due to dehydration, smoking, or living at high altitude.",
            "normal": "Great news! Your hemoglobin level is perfect, which means your blood is carrying oxygen efficiently throughout your body."
        },
        "conditions": {
            "low": ["Iron-deficiency anemia", "Chronic disease anemia", "Blood loss", "Kidney disease"],
            "high": ["Dehydration", "Smoking effects", "High altitude living", "Blood disorders"]
        },
        "recommendations": {
            "low": {
                "foods_to_eat": ["Red meat (beef, lamb)", "Dark leafy greens (spinach, kale)", "Beans and lentils", "Iron-fortified cereals", "Dark chocolate", "Tofu", "Cashews and almonds"],
                "foods_to_avoid": ["Tea and coffee with meals (blocks iron)", "Dairy products with iron-rich meals", "Whole grains with iron (contains phytates)"],
                "lifestyle": ["Take vitamin C with iron-rich foods", "Cook in cast iron pans", "Get 7-8 hours sleep", "Avoid smoking", "Consult doctor about iron supplements"],
                "activities": ["Light exercise like walking", "Breathing exercises", "Avoid intense workouts until levels improve"]
            },
            "high": {
                "foods_to_eat": ["Plenty of water (8-10 glasses daily)", "Fresh fruits and vegetables", "Whole grains", "Lean proteins"],
                "foods_to_avoid": ["Excessive red meat", "Alcohol", "Processed foods"],
                "lifestyle": ["Stay well hydrated", "Quit smoking immediately", "Monitor blood pressure", "Regular medical check-ups"],
                "activities": ["Moderate cardio exercise", "Swimming", "Yoga and meditation"]
            },
            "normal": {
                "foods_to_eat": ["Balanced diet with iron-rich foods", "Vitamin C sources (citrus fruits)", "Leafy green vegetables"],
                "foods_to_avoid": ["Excessive processed foods", "Too much caffeine"],
                "lifestyle": ["Maintain current healthy habits", "Regular exercise", "Annual health check-ups"],
                "activities": ["Continue current exercise routine", "Stay active with sports/hobbies"]
            }
        }
    },

    "wbc": {
        "displayName": "White Blood Cells (Infection Fighters)",
        "unit": "cells/μL",
        "aliases": ["white blood cells", "leukocytes", "wbc count", "white cell count", "total wbc", "infection fighters"],
        "ranges": {"default": [4500, 11000]},
        "category": "immune_system",
        "organ_systems": ["immune", "blood"],
        "simple_explanation": {
            "what_it_is": "White blood cells are your body's army that fights off infections, viruses, and bacteria.",
            "why_important": "They protect you from getting sick and help you recover when you do get ill."
        },
        "interpretation": {
            "low": "Your white blood cell count is low, which means your immune system might be weakened. You could be more likely to get infections.",
            "high": "Your white blood cell count is high, which usually means your body is fighting an infection or inflammation right now.",
            "normal": "Excellent! Your white blood cell count is normal, showing your immune system is strong and ready to protect you."
        },
        "conditions": {
            "low": ["Weakened immune system", "Viral infections", "Autoimmune disorders", "Medication side effects"],
            "high": ["Bacterial infection", "Viral infection", "Inflammatory conditions", "Stress response", "Smoking effects"]
        },
        "recommendations": {
            "low": {
                "foods_to_eat": ["Citrus fruits (oranges, lemons)", "Garlic and ginger", "Yogurt with probiotics", "Green tea", "Almonds and sunflower seeds", "Broccoli and spinach", "Sweet potatoes"],
                "foods_to_avoid": ["Processed foods", "Excessive sugar", "Alcohol", "Fast food"],
                "lifestyle": ["Get 7-9 hours sleep", "Manage stress", "Wash hands frequently", "Avoid crowded places during flu season", "Stay warm in cold weather"],
                "activities": ["Light to moderate exercise", "Meditation", "Avoid overexertion", "Indoor activities during illness seasons"]
            },
            "high": {
                "foods_to_eat": ["Anti-inflammatory foods", "Turmeric and ginger", "Green leafy vegetables", "Berries", "Fatty fish (salmon, mackerel)", "Plenty of water"],
                "foods_to_avoid": ["Processed foods", "Excessive sugar", "Fried foods", "Alcohol"],
                "lifestyle": ["Rest and get extra sleep", "Stay hydrated", "Take prescribed medications", "Monitor temperature", "Follow up with doctor"],
                "activities": ["Rest and avoid strenuous exercise", "Light stretching", "Meditation for stress relief"]
            },
            "normal": {
                "foods_to_eat": ["Balanced diet rich in vitamins", "Colorful fruits and vegetables", "Whole grains", "Lean proteins"],
                "foods_to_avoid": ["Excessive processed foods", "Too much sugar"],
                "lifestyle": ["Maintain good hygiene", "Regular sleep schedule", "Stress management", "Regular exercise"],
                "activities": ["Regular exercise routine", "Outdoor activities", "Social activities for mental health"]
            }
        }
    },

    "glucose": {
        "displayName": "Blood Sugar (Energy Level)",
        "unit": "mg/dL",
        "aliases": ["blood sugar", "glucose level", "fasting glucose", "sugar", "blood glucose", "diabetes test"],
        "ranges": {"default": [70, 100], "prediabetic": [100, 125], "diabetic": [126, 400]},
        "category": "metabolism",
        "organ_systems": ["endocrine", "metabolic", "cardiovascular"],
        "simple_explanation": {
            "what_it_is": "Blood sugar is the amount of glucose (sugar) in your blood, which your body uses for energy.",
            "why_important": "Your body needs the right amount of sugar for energy, but too much or too little can cause serious health problems."
        },
        "interpretation": {
            "low": "Your blood sugar is low (hypoglycemia). This can make you feel dizzy, shaky, or confused. You need to eat something soon.",
            "high": "Your blood sugar is high, which may indicate diabetes or prediabetes. This is serious and needs immediate attention from a doctor.",
            "normal": "Perfect! Your blood sugar is in the healthy range, which means your body is managing energy well."
        },
        "conditions": {
            "low": ["Hypoglycemia", "Skipping meals", "Too much insulin", "Excessive exercise", "Alcohol consumption"],
            "high": ["Type 2 diabetes", "Prediabetes", "Type 1 diabetes", "Stress", "Illness", "Certain medications"]
        },
        "recommendations": {
            "low": {
                "foods_to_eat": ["Complex carbs (oats, quinoa)", "Protein with each meal", "Healthy snacks (nuts, fruits)", "Regular small meals", "Peanut butter", "Greek yogurt"],
                "foods_to_avoid": ["Skipping meals", "Excessive alcohol", "Simple sugars alone", "Long periods without eating"],
                "lifestyle": ["Eat regular meals", "Carry healthy snacks", "Monitor blood sugar", "Don't skip breakfast", "Limit alcohol"],
                "activities": ["Regular, moderate exercise", "Avoid intense fasting workouts", "Monitor during exercise"]
            },
            "high": {
                "foods_to_eat": ["Low glycemic foods", "Non-starchy vegetables", "Lean proteins (chicken, fish)", "Whole grains in moderation", "Nuts and seeds", "Berries", "Leafy greens"],
                "foods_to_avoid": ["Sugary drinks and sodas", "White bread and rice", "Pastries and sweets", "Processed foods", "Fried foods", "Fruit juices"],
                "lifestyle": ["Lose excess weight", "Check blood sugar regularly", "Take medications as prescribed", "Stay hydrated with water", "Quit smoking"],
                "activities": ["30 minutes daily exercise", "Walking after meals", "Strength training", "Yoga", "Swimming"]
            },
            "normal": {
                "foods_to_eat": ["Balanced meals", "Whole grains", "Fresh fruits and vegetables", "Lean proteins", "Healthy fats"],
                "foods_to_avoid": ["Excessive sugary foods", "Large portions", "Processed snacks"],
                "lifestyle": ["Maintain healthy weight", "Regular meal times", "Stay active", "Annual diabetes screening"],
                "activities": ["Regular exercise routine", "Stay active throughout day", "Enjoy variety of physical activities"]
            }
        }
    },

    "cholesterol": {
        "displayName": "Total Cholesterol (Heart Health Indicator)",
        "unit": "mg/dL",
        "aliases": ["cholesterol", "total cholesterol", "chol", "heart health", "lipid"],
        "ranges": {"default": [0, 200], "borderline": [200, 239], "high": [240, 500]},
        "category": "heart_health",
        "organ_systems": ["cardiovascular"],
        "simple_explanation": {
            "what_it_is": "Cholesterol is a waxy substance in your blood. Your body needs some, but too much can clog your arteries like grease in pipes.",
            "why_important": "High cholesterol increases your risk of heart attacks and strokes by blocking blood flow to your heart and brain."
        },
        "interpretation": {
            "low": "Your cholesterol is low, which is generally great for your heart health! Keep up the good work.",
            "high": "Your cholesterol is high, which increases your risk of heart disease and stroke. This needs attention through diet and lifestyle changes.",
            "normal": "Excellent! Your cholesterol is in the healthy range, which is great for your heart and blood vessels."
        },
        "conditions": {
            "low": ["Generally healthy", "Good diet and exercise", "Genetic factors"],
            "high": ["Risk of heart disease", "Risk of stroke", "Atherosclerosis", "Family history", "Poor diet", "Lack of exercise"]
        },
        "recommendations": {
            "high": {
                "foods_to_eat": ["Oats and barley", "Beans and legumes", "Nuts (almonds, walnuts)", "Fatty fish (salmon, sardines)", "Olive oil", "Avocados", "Apples and citrus fruits", "Soy products"],
                "foods_to_avoid": ["Red meat", "Full-fat dairy", "Fried foods", "Trans fats", "Processed meats", "Baked goods", "Fast food"],
                "lifestyle": ["Lose excess weight", "Quit smoking", "Limit alcohol", "Manage stress", "Get regular check-ups"],
                "activities": ["30 minutes cardio daily", "Brisk walking", "Swimming", "Cycling", "Dancing", "Strength training"]
            },
            "normal": {
                "foods_to_eat": ["Heart-healthy Mediterranean diet", "Fish twice a week", "Plenty of fruits and vegetables", "Whole grains", "Nuts in moderation"],
                "foods_to_avoid": ["Excessive saturated fats", "Trans fats", "Processed foods"],
                "lifestyle": ["Maintain healthy weight", "Don't smoke", "Moderate alcohol", "Regular exercise", "Annual lipid screening"],
                "activities": ["Continue regular exercise", "Try new heart-healthy activities", "Stay active daily"]
            }
        }
    },

    "triglycerides": {
        "displayName": "Triglycerides (Fat in Blood)",
        "unit": "mg/dL",
        "aliases": ["triglyceride", "tg", "trigs", "blood fats"],
        "ranges": {"default": [0, 150], "borderline": [150, 199], "high": [200, 500]},
        "category": "heart_health",
        "organ_systems": ["cardiovascular", "metabolic"],
        "simple_explanation": {
            "what_it_is": "Triglycerides are fats in your blood that your body uses for energy. Too much can be harmful to your heart.",
            "why_important": "High triglycerides increase your risk of heart disease and can cause inflammation in your pancreas."
        },
        "interpretation": {
            "low": "Great! Your triglycerides are low, which is excellent for your heart health.",
            "high": "Your triglycerides are high, which increases your risk of heart disease and pancreatitis. Diet and lifestyle changes can help.",
            "normal": "Perfect! Your triglyceride levels are healthy, showing good fat metabolism."
        },
        "conditions": {
            "high": ["Risk of heart disease", "Risk of pancreatitis", "Metabolic syndrome", "Diabetes", "Obesity"]
        },
        "recommendations": {
            "high": {
                "foods_to_eat": ["Omega-3 rich fish", "Whole grains", "Vegetables", "Fruits", "Lean proteins", "Beans and legumes"],
                "foods_to_avoid": ["Simple carbs and sugars", "Alcohol", "Fried foods", "Processed foods", "Sugary drinks", "White bread and pasta"],
                "lifestyle": ["Lose excess weight", "Limit alcohol severely", "Control diabetes if present", "Don't smoke"],
                "activities": ["Regular aerobic exercise", "Walking", "Swimming", "Cycling", "30+ minutes daily"]
            },
            "normal": {
                "foods_to_eat": ["Continue healthy balanced diet", "Fish twice weekly", "Whole grains", "Fruits and vegetables"],
                "foods_to_avoid": ["Excessive simple sugars", "Too much alcohol", "Processed foods"],
                "lifestyle": ["Maintain healthy weight", "Moderate alcohol", "Regular exercise", "Stress management"],
                "activities": ["Keep up regular exercise routine", "Try new physical activities"]
            }
        }
    },

    "creatinine": {
        "displayName": "Creatinine (Kidney Function Test)",
        "unit": "mg/dL",
        "aliases": ["creatinine level", "serum creatinine", "kidney function", "kidney test"],
        "ranges": {"default": [0.6, 1.2], "male": [0.7, 1.3], "female": [0.6, 1.1]},
        "category": "kidney_health",
        "organ_systems": ["renal", "urinary"],
        "simple_explanation": {
            "what_it_is": "Creatinine is a waste product that your kidneys filter out of your blood. It shows how well your kidneys are working.",
            "why_important": "High creatinine means your kidneys aren't cleaning your blood properly, which can be dangerous."
        },
        "interpretation": {
            "low": "Your creatinine is low, which is usually not a concern. It might indicate low muscle mass.",
            "high": "Your creatinine is high, which suggests your kidneys aren't working properly. This needs immediate medical attention.",
            "normal": "Excellent! Your creatinine level is normal, showing your kidneys are filtering waste effectively."
        },
        "conditions": {
            "high": ["Kidney disease", "Kidney failure", "Dehydration", "High blood pressure damage", "Diabetes complications"]
        },
        "recommendations": {
            "high": {
                "foods_to_eat": ["Low-sodium foods", "Fresh fruits and vegetables", "Whole grains", "Limited protein (as advised by doctor)"],
                "foods_to_avoid": ["High-sodium foods", "Processed foods", "Excessive protein", "Phosphorus-rich foods", "Potassium-rich foods (if advised)"],
                "lifestyle": ["Control blood pressure", "Manage diabetes", "Stay hydrated (unless restricted)", "Avoid NSAIDs", "Follow kidney diet"],
                "activities": ["Light to moderate exercise", "Walking", "Avoid dehydration during exercise", "Follow doctor's activity guidelines"]
            },
            "normal": {
                "foods_to_eat": ["Balanced healthy diet", "Plenty of water", "Fruits and vegetables", "Whole grains"],
                "foods_to_avoid": ["Excessive salt", "Too much protein", "Processed foods"],
                "lifestyle": ["Stay well hydrated", "Control blood pressure", "Maintain healthy weight", "Don't smoke"],
                "activities": ["Regular exercise", "Stay active", "Drink water during workouts"]
            }
        }
    },

    "alt": {
        "displayName": "ALT (Liver Function Test)",
        "unit": "U/L",
        "aliases": ["alanine aminotransferase", "sgpt", "alanine transaminase", "liver enzyme", "liver function"],
        "ranges": {"default": [7, 45], "male": [10, 50], "female": [7, 35]},
        "category": "liver_health",
        "organ_systems": ["hepatic", "digestive"],
        "simple_explanation": {
            "what_it_is": "ALT is an enzyme found mainly in your liver. High levels mean your liver cells are damaged or inflamed.",
            "why_important": "Your liver cleans toxins from your body. Damage to it can be serious and affect your overall health."
        },
        "interpretation": {
            "low": "Your ALT is low, which is generally good and shows minimal liver stress.",
            "high": "Your ALT is high, which indicates liver cell damage or inflammation. This could be from various causes and needs medical evaluation.",
            "normal": "Great! Your ALT level is normal, showing your liver is healthy and functioning well."
        },
        "conditions": {
            "high": ["Liver damage", "Hepatitis", "Fatty liver disease", "Alcohol damage", "Medication effects", "Viral infections"]
        },
        "recommendations": {
            "high": {
                "foods_to_eat": ["Leafy green vegetables", "Berries and antioxidant-rich fruits", "Green tea", "Nuts and seeds", "Fatty fish", "Whole grains", "Turmeric"],
                "foods_to_avoid": ["Alcohol completely", "Processed foods", "Fried foods", "High-fat foods", "Excessive sugar", "Acetaminophen (unless prescribed)"],
                "lifestyle": ["Stop drinking alcohol", "Lose excess weight", "Avoid unnecessary medications", "Get hepatitis vaccines", "Practice safe habits"],
                "activities": ["Light to moderate exercise", "Walking", "Yoga", "Avoid strenuous exercise until levels improve"]
            },
            "normal": {
                "foods_to_eat": ["Liver-friendly foods", "Antioxidant-rich fruits", "Vegetables", "Whole grains", "Lean proteins"],
                "foods_to_avoid": ["Excessive alcohol", "Processed foods", "Unnecessary medications"],
                "lifestyle": ["Moderate alcohol consumption", "Maintain healthy weight", "Avoid risky behaviors", "Regular check-ups"],
                "activities": ["Regular exercise routine", "Stay active", "Enjoy variety of activities"]
            }
        }
    },

    "tsh": {
        "displayName": "TSH (Thyroid Function)",
        "unit": "mIU/L",
        "aliases": ["thyroid stimulating hormone", "thyrotropin", "thyroid function", "thyroid test"],
        "ranges": {"default": [0.4, 4.0]},
        "category": "hormones",
        "organ_systems": ["endocrine", "metabolic"],
        "simple_explanation": {
            "what_it_is": "TSH is a hormone that tells your thyroid gland how much thyroid hormone to make. It controls your body's metabolism.",
            "why_important": "Thyroid hormones control how fast your body uses energy, affecting weight, heart rate, mood, and energy levels."
        },
        "interpretation": {
            "low": "Your TSH is low, which may mean your thyroid is overactive (hyperthyroidism). This can cause rapid heartbeat, weight loss, and anxiety.",
            "high": "Your TSH is high, which may mean your thyroid is underactive (hypothyroidism). This can cause fatigue, weight gain, and depression.",
            "normal": "Perfect! Your TSH level is normal, showing your thyroid is working properly to control your metabolism."
        },
        "conditions": {
            "low": ["Hyperthyroidism", "Overactive thyroid", "Graves' disease", "Thyroid nodules"],
            "high": ["Hypothyroidism", "Underactive thyroid", "Hashimoto's disease", "Iodine deficiency"]
        },
        "recommendations": {
            "low": {
                "foods_to_eat": ["Calcium-rich foods", "Berries", "Leafy greens", "Whole grains", "Lean proteins"],
                "foods_to_avoid": ["Excessive iodine", "Caffeine", "Alcohol", "Processed foods", "Soy products"],
                "lifestyle": ["Take prescribed medications", "Manage stress", "Get regular sleep", "Avoid smoking", "Regular monitoring"],
                "activities": ["Moderate exercise", "Yoga and meditation", "Avoid overexertion", "Swimming"]
            },
            "high": {
                "foods_to_eat": ["Iodine-rich foods (seaweed, fish)", "Brazil nuts (selenium)", "Dairy products", "Eggs", "Fruits and vegetables"],
                "foods_to_avoid": ["Excessive soy products", "Raw cruciferous vegetables", "Processed foods"],
                "lifestyle": ["Take thyroid medication as prescribed", "Maintain regular sleep", "Manage stress", "Regular monitoring"],
                "activities": ["Regular exercise (boosts metabolism)", "Walking", "Swimming", "Strength training"]
            },
            "normal": {
                "foods_to_eat": ["Balanced diet", "Iodine sources in moderation", "Fruits and vegetables", "Whole grains"],
                "foods_to_avoid": ["Excessive processed foods", "Too much soy"],
                "lifestyle": ["Maintain healthy habits", "Regular sleep schedule", "Stress management", "Annual thyroid screening"],
                "activities": ["Continue regular exercise", "Stay active", "Enjoy variety of activities"]
            }
        }
    }
}

# ORGAN SYSTEM HEALTH GUIDE - Built from scratch
ORGAN_SYSTEMS_GUIDE = {
    "cardiovascular": {
        "name": "Heart & Blood Vessels",
        "icon": "❤️",
        "description": "Your cardiovascular system pumps blood and delivers oxygen and nutrients to every part of your body",
        "affected_by": ["hemoglobin", "cholesterol", "triglycerides", "glucose"],
        "health_tips": [
            "Exercise for 30 minutes daily to strengthen your heart",
            "Eat heart-healthy foods like fish, nuts, and vegetables",
            "Limit salt to less than 2,300mg per day",
            "Don't smoke - it damages blood vessels immediately",
            "Manage stress through meditation or hobbies",
            "Get 7-8 hours of sleep for heart recovery"
        ],
        "warning_signs": ["Chest pain", "Shortness of breath", "Irregular heartbeat", "Swelling in legs", "Extreme fatigue"],
        "emergency_advice": "Call emergency services immediately if you experience chest pain, difficulty breathing, or think you're having a heart attack."
    },
    "immune": {
        "name": "Immune Defense System",
        "icon": "🛡️",
        "description": "Your immune system is your body's army that fights infections, viruses, and keeps you healthy",
        "affected_by": ["wbc"],
        "health_tips": [
            "Get 7-9 hours of quality sleep to boost immunity",
            "Eat colorful fruits and vegetables rich in vitamins",
            "Exercise regularly but don't overdo it",
            "Wash hands frequently with soap for 20 seconds",
            "Manage stress - chronic stress weakens immunity",
            "Stay hydrated with plenty of water",
            "Get recommended vaccinations"
        ],
        "warning_signs": ["Frequent infections", "Slow healing", "Constant fatigue", "Digestive issues"],
        "emergency_advice": "Seek medical attention if you have signs of serious infection like high fever, difficulty breathing, or severe weakness."
    },
    "metabolic": {
        "name": "Metabolism & Energy System",
        "icon": "⚡",
        "description": "Your metabolic system controls how your body uses food for energy and maintains blood sugar levels",
        "affected_by": ["glucose", "tsh"],
        "health_tips": [
            "Eat regular, balanced meals to maintain steady blood sugar",
            "Choose complex carbohydrates over simple sugars",
            "Include protein with each meal",
            "Stay physically active throughout the day",
            "Limit processed foods and sugary drinks",
            "Maintain a healthy weight",
            "Don't skip breakfast"
        ],
        "warning_signs": ["Extreme thirst", "Frequent urination", "Unexplained weight changes", "Constant fatigue", "Blurred vision"],
        "emergency_advice": "Seek immediate medical care for signs of diabetic emergency like confusion, vomiting, or extremely high/low blood sugar."
    },
    "renal": {
        "name": "Kidney & Urinary System",
        "icon": "🫘",
        "description": "Your kidneys filter waste from your blood and maintain proper fluid balance in your body",
        "affected_by": ["creatinine"],
        "health_tips": [
            "Drink 8-10 glasses of water daily",
            "Limit sodium to protect kidney function",
            "Control blood pressure and diabetes",
            "Avoid overuse of pain medications (NSAIDs)",
            "Don't hold urine - go when you need to",
            "Eat kidney-friendly foods",
            "Get regular kidney function tests if at risk"
        ],
        "warning_signs": ["Swelling in legs/face", "Changes in urination", "Blood in urine", "High blood pressure", "Persistent fatigue"],
        "emergency_advice": "Seek immediate care for severe swelling, inability to urinate, or signs of kidney failure."
    },
    "hepatic": {
        "name": "Liver Health System",
        "icon": "🫀",
        "description": "Your liver processes nutrients, makes proteins, and removes toxins from your body",
        "affected_by": ["alt"],
        "health_tips": [
            "Limit alcohol consumption or avoid completely",
            "Maintain a healthy weight to prevent fatty liver",
            "Eat antioxidant-rich foods like berries and green tea",
            "Avoid unnecessary medications and supplements",
            "Get vaccinated against hepatitis A and B",
            "Practice safe behaviors to avoid infections",
            "Exercise regularly to improve liver health"
        ],
        "warning_signs": ["Yellowing of skin/eyes", "Abdominal pain", "Dark urine", "Light-colored stools", "Persistent fatigue"],
        "emergency_advice": "Seek immediate medical attention for jaundice (yellowing), severe abdominal pain, or signs of liver failure."
    },
    "blood": {
        "name": "Blood & Circulation System",
        "icon": "🩸",
        "description": "Your blood carries oxygen, nutrients, and immune cells throughout your body",
        "affected_by": ["hemoglobin", "wbc"],
        "health_tips": [
            "Eat iron-rich foods like lean meat and spinach",
            "Include vitamin C to help absorb iron",
            "Stay hydrated for proper blood volume",
            "Exercise to improve circulation",
            "Don't smoke - it affects blood oxygen",
            "Manage stress to support healthy blood pressure",
            "Get regular blood tests to monitor health"
        ],
        "warning_signs": ["Extreme fatigue", "Pale skin", "Frequent infections", "Easy bruising", "Shortness of breath"],
        "emergency_advice": "Seek immediate care for severe weakness, difficulty breathing, or signs of serious blood loss."
    }
}

# DISEASE CONDITIONS DATABASE - Built from scratch
DISEASE_CONDITIONS = {
    "anemia": {
        "name": "Anemia (Low Blood Iron)",
        "description": "A condition where you don't have enough healthy red blood cells to carry oxygen to your body's tissues",
        "symptoms": ["Fatigue and weakness", "Pale skin", "Cold hands and feet", "Brittle nails", "Strange cravings (ice, starch)"],
        "causes": ["Iron deficiency", "Blood loss", "Chronic disease", "Poor diet"],
        "severity": "Moderate - can significantly impact quality of life",
        "treatment_approach": "Usually treatable with diet changes and supplements",
        "foods_to_eat": ["Red meat", "Dark leafy greens", "Beans and lentils", "Iron-fortified cereals", "Dark chocolate", "Cashews"],
        "foods_to_avoid": ["Tea/coffee with meals", "Dairy with iron-rich foods", "Calcium supplements with iron"],
        "lifestyle_changes": ["Take iron supplements as prescribed", "Eat vitamin C with iron", "Cook in cast iron", "Get adequate sleep"],
        "when_to_see_doctor": "If symptoms persist despite dietary changes, or if you experience severe fatigue"
    },
    "diabetes": {
        "name": "Diabetes (High Blood Sugar)",
        "description": "A group of diseases that result in too much sugar in the blood, which can damage organs over time",
        "symptoms": ["Increased thirst", "Frequent urination", "Extreme fatigue", "Blurred vision", "Slow healing cuts"],
        "causes": ["Insulin resistance", "Genetics", "Obesity", "Sedentary lifestyle", "Poor diet"],
        "severity": "Serious - requires lifelong management",
        "treatment_approach": "Managed through diet, exercise, medication, and blood sugar monitoring",
        "foods_to_eat": ["Non-starchy vegetables", "Whole grains", "Lean proteins", "Healthy fats", "Low-glycemic fruits"],
        "foods_to_avoid": ["Sugary drinks", "White bread/rice", "Processed foods", "Sweets and desserts", "Fried foods"],
        "lifestyle_changes": ["Regular blood sugar monitoring", "Daily exercise", "Weight management", "Stress reduction", "Regular medical check-ups"],
        "when_to_see_doctor": "Immediately if blood sugar is very high, or for regular diabetes management"
    },
    "high_cholesterol": {
        "name": "High Cholesterol (Heart Disease Risk)",
        "description": "Too much cholesterol in blood can build up in arteries and increase risk of heart attack and stroke",
        "symptoms": ["Usually no symptoms", "May cause chest pain", "Yellow deposits around eyes"],
        "causes": ["Poor diet", "Lack of exercise", "Genetics", "Smoking", "Age"],
        "severity": "Moderate to High - increases heart disease risk",
        "treatment_approach": "Lifestyle changes and sometimes medication",
        "foods_to_eat": ["Oats", "Fish", "Nuts", "Olive oil", "Fruits and vegetables", "Whole grains"],
        "foods_to_avoid": ["Red meat", "Full-fat dairy", "Fried foods", "Trans fats", "Processed meats"],
        "lifestyle_changes": ["30 minutes daily exercise", "Weight loss if needed", "Quit smoking", "Limit alcohol"],
        "when_to_see_doctor": "For initial diagnosis and if lifestyle changes don't improve levels"
    },
    "kidney_disease": {
        "name": "Kidney Disease (Reduced Kidney Function)",
        "description": "Kidneys are damaged and can't filter blood as well as they should, leading to waste buildup",
        "symptoms": ["Swelling in legs/ankles", "Fatigue", "Changes in urination", "Nausea", "High blood pressure"],
        "causes": ["Diabetes", "High blood pressure", "Infections", "Genetic disorders", "Medications"],
        "severity": "Serious - can progress to kidney failure",
        "treatment_approach": "Slow progression through diet, medication, and lifestyle changes",
        "foods_to_eat": ["Low-sodium foods", "Limited protein", "Fruits and vegetables (as allowed)", "Whole grains"],
        "foods_to_avoid": ["High-sodium foods", "Processed foods", "Excessive protein", "High-phosphorus foods"],
        "lifestyle_changes": ["Control blood pressure and diabetes", "Limit protein", "Stay hydrated", "Avoid NSAIDs"],
        "when_to_see_doctor": "Immediately for severe symptoms, regularly for monitoring"
    },
    "liver_disease": {
        "name": "Liver Disease (Liver Damage)",
        "description": "Damage to the liver that affects its ability to function properly in processing nutrients and toxins",
        "symptoms": ["Fatigue", "Abdominal pain", "Yellowing of skin/eyes", "Dark urine", "Nausea"],
        "causes": ["Alcohol abuse", "Viral hepatitis", "Fatty liver disease", "Medications", "Genetics"],
        "severity": "Moderate to Severe - can be life-threatening",
        "treatment_approach": "Remove causes, supportive care, lifestyle changes, sometimes medication",
        "foods_to_eat": ["Fruits and vegetables", "Whole grains", "Lean proteins", "Healthy fats", "Green tea"],
        "foods_to_avoid": ["Alcohol completely", "High-fat foods", "Processed foods", "Excessive sugar"],
        "lifestyle_changes": ["Stop drinking alcohol", "Weight loss", "Avoid unnecessary medications", "Regular monitoring"],
        "when_to_see_doctor": "Immediately for jaundice or severe symptoms, regularly for monitoring"
    },
    "thyroid_disorders": {
        "name": "Thyroid Disorders (Hormone Imbalance)",
        "description": "Problems with the thyroid gland that affect metabolism, energy, and many body functions",
        "symptoms": ["Weight changes", "Energy changes", "Heart rate changes", "Mood changes", "Temperature sensitivity"],
        "causes": ["Autoimmune conditions", "Iodine deficiency/excess", "Genetics", "Stress", "Infections"],
        "severity": "Moderate - affects quality of life but treatable",
        "treatment_approach": "Hormone replacement or anti-thyroid medications, lifestyle support",
        "foods_to_eat": ["Iodine-rich foods (if deficient)", "Selenium-rich foods", "Fruits and vegetables", "Whole grains"],
        "foods_to_avoid": ["Excessive soy", "Raw cruciferous vegetables (if hypothyroid)", "Processed foods"],
        "lifestyle_changes": ["Take medications as prescribed", "Regular monitoring", "Stress management", "Adequate sleep"],
        "when_to_see_doctor": "For initial symptoms and regular monitoring of treatment"
    }
}

# SIMPLE TEXT EXTRACTION - Rule-based approach (HACKATHON COMPLIANT)
def extract_medical_values_comprehensive(text):
    """
    Advanced rule-based medical value extraction built from scratch
    No AI models used - pure pattern matching and logic
    """
    text_lower = text.lower().strip()
    extracted_values = {}

    # Enhanced patterns for each medical test
    for test_key, test_info in MEDICAL_KNOWLEDGE_DATABASE.items():
        test_names = [test_info["displayName"].lower()] + [alias.lower() for alias in test_info["aliases"]]

        for name in test_names:
            # Pattern variations for better extraction
            patterns = [
                rf'{re.escape(name)}\s*:?\s*(\d+\.?\d*)\s*{re.escape(test_info["unit"].lower())}?',
                rf'{re.escape(name)}\s*=\s*(\d+\.?\d*)',
                rf'{re.escape(name)}\s*-\s*(\d+\.?\d*)',
                rf'(\d+\.?\d*)\s*{re.escape(test_info["unit"].lower())}?\s*{re.escape(name)}'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    try:
                        value = float(matches[0])
                        # Reasonable range validation
                        if 0.01 <= value <= 50000:  # Expanded range for various tests
                            extracted_values[test_key] = value
                            break
                    except (ValueError, TypeError):
                        continue

            if test_key in extracted_values:
                break

    return extracted_values

def identify_health_conditions(extracted_data):
    """
    Identify potential health conditions based on test results
    Built from scratch rule-based diagnostic logic
    """
    identified_conditions = []

    for test_key, value in extracted_data.items():
        if test_key in MEDICAL_KNOWLEDGE_DATABASE:
            test_info = MEDICAL_KNOWLEDGE_DATABASE[test_key]
            ranges = test_info["ranges"]["default"]

            if value < ranges[0] or value > ranges[1]:
                conditions = test_info["conditions"].get("low" if value < ranges[0] else "high", [])
                for condition in conditions:
                    # Map to our disease database
                    if "anemia" in condition.lower() and "anemia" not in [c["key"] for c in identified_conditions]:
                        identified_conditions.append({"key": "anemia", "confidence": "High" if value < ranges[0] * 0.8 else "Moderate"})
                    elif "diabetes" in condition.lower() and "diabetes" not in [c["key"] for c in identified_conditions]:
                        identified_conditions.append({"key": "diabetes", "confidence": "High" if value > ranges[1] * 1.3 else "Moderate"})
                    elif "heart disease" in condition.lower() and "high_cholesterol" not in [c["key"] for c in identified_conditions]:
                        identified_conditions.append({"key": "high_cholesterol", "confidence": "High" if value > ranges[1] * 1.2 else "Moderate"})
                    elif "kidney" in condition.lower() and "kidney_disease" not in [c["key"] for c in identified_conditions]:
                        identified_conditions.append({"key": "kidney_disease", "confidence": "High" if value > ranges[1] * 1.5 else "Moderate"})
                    elif "liver" in condition.lower() and "liver_disease" not in [c["key"] for c in identified_conditions]:
                        identified_conditions.append({"key": "liver_disease", "confidence": "High" if value > ranges[1] * 2 else "Moderate"})
                    elif "thyroid" in condition.lower() and "thyroid_disorders" not in [c["key"] for c in identified_conditions]:
                        identified_conditions.append({"key": "thyroid_disorders", "confidence": "Moderate"})

    return identified_conditions

def generate_comprehensive_health_report(extracted_data):
    """
    Generate a comprehensive, patient-friendly health report
    Built from scratch with extensive recommendations
    """
    if not extracted_data:
        return {
            "message": "I couldn't find any medical test values in your report. Please make sure to include test names with their values (like 'Hemoglobin: 12.5 g/dL').",
            "suggestion": "Try typing your test results in this format: 'Test Name: Value Unit' for each test.",
            "individual_tests": [],
            "health_conditions": [],
            "organ_analysis": {},
            "health_score": 0,
            "overall_recommendations": []
        }

    # Analyze individual tests
    individual_analyses = []
    organ_impact = {}
    abnormal_count = 0
    all_recommendations = {
        "foods_to_eat": set(),
        "foods_to_avoid": set(),
        "lifestyle": set(),
        "activities": set()
    }

    for test_key, value in extracted_data.items():
        if test_key in MEDICAL_KNOWLEDGE_DATABASE:
            test_info = MEDICAL_KNOWLEDGE_DATABASE[test_key]
            ranges = test_info["ranges"]["default"]

            # Determine status
            if value < ranges[0]:
                status = "LOW"
                status_emoji = "🔻"
                interpretation = test_info["interpretation"]["low"]
                recommendations = test_info["recommendations"]["low"]
                abnormal_count += 1
            elif value > ranges[1]:
                status = "HIGH"
                status_emoji = "🔺"  
                interpretation = test_info["interpretation"]["high"]
                recommendations = test_info["recommendations"]["high"]
                abnormal_count += 1
            else:
                status = "NORMAL"
                status_emoji = "✅"
                interpretation = test_info["interpretation"]["normal"]
                recommendations = test_info["recommendations"]["normal"]

            # Create detailed analysis
            analysis = {
                "test_name": test_info["displayName"],
                "simple_explanation": test_info["simple_explanation"],
                "value": value,
                "unit": test_info["unit"],
                "status": status,
                "status_emoji": status_emoji,
                "reference_range": f"{ranges[0]}-{ranges[1]}",
                "interpretation": interpretation,
                "recommendations": recommendations,
                "category": test_info["category"]
            }

            individual_analyses.append(analysis)

            # Collect recommendations
            for rec_type in all_recommendations.keys():
                if rec_type in recommendations:
                    all_recommendations[rec_type].update(recommendations[rec_type][:3])  # Top 3 from each

            # Track organ system impact
            for organ in test_info["organ_systems"]:
                if organ not in organ_impact:
                    organ_impact[organ] = {"affected_tests": [], "normal_tests": [], "total_score": 0}

                if status != "NORMAL":
                    organ_impact[organ]["affected_tests"].append(analysis)
                    organ_impact[organ]["total_score"] += (2 if status == "HIGH" else 1)
                else:
                    organ_impact[organ]["normal_tests"].append(analysis)

    # Identify potential health conditions
    health_conditions = identify_health_conditions(extracted_data)
    condition_details = []

    for condition in health_conditions:
        if condition["key"] in DISEASE_CONDITIONS:
            condition_info = DISEASE_CONDITIONS[condition["key"]]
            condition_details.append({
                "name": condition_info["name"],
                "description": condition_info["description"],
                "confidence": condition["confidence"],
                "symptoms": condition_info["symptoms"],
                "severity": condition_info["severity"],
                "treatment_approach": condition_info["treatment_approach"],
                "recommendations": {
                    "foods_to_eat": condition_info["foods_to_eat"],
                    "foods_to_avoid": condition_info["foods_to_avoid"],
                    "lifestyle_changes": condition_info["lifestyle_changes"]
                },
                "when_to_see_doctor": condition_info["when_to_see_doctor"]
            })

    # Calculate health score
    total_tests = len(extracted_data)
    health_score = max(0, int(((total_tests - abnormal_count) / total_tests) * 100)) if total_tests > 0 else 0

    # Organize organ system analysis
    organ_analysis = {}
    for organ_key, impact_data in organ_impact.items():
        if organ_key in ORGAN_SYSTEMS_GUIDE:
            organ_info = ORGAN_SYSTEMS_GUIDE[organ_key]
            affected_count = len(impact_data["affected_tests"])

            if affected_count > 0:
                if impact_data["total_score"] >= 3:
                    organ_status = "NEEDS IMMEDIATE ATTENTION"
                    status_color = "danger"
                else:
                    organ_status = "NEEDS ATTENTION"
                    status_color = "warning"
            else:
                organ_status = "HEALTHY"
                status_color = "success"

            organ_analysis[organ_key] = {
                "info": organ_info,
                "status": organ_status,
                "status_color": status_color,
                "affected_tests": impact_data["affected_tests"],
                "normal_tests": impact_data["normal_tests"],
                "affected_count": affected_count,
                "severity_score": impact_data["total_score"]
            }

    # Convert sets to lists for JSON serialization
    overall_recommendations = {
        "foods_to_eat": list(all_recommendations["foods_to_eat"])[:8],
        "foods_to_avoid": list(all_recommendations["foods_to_avoid"])[:8],
        "lifestyle": list(all_recommendations["lifestyle"])[:8],
        "activities": list(all_recommendations["activities"])[:8]
    }

    return {
        "individual_tests": individual_analyses,
        "health_conditions": condition_details,
        "organ_analysis": organ_analysis,
        "health_score": health_score,
        "total_tests": total_tests,
        "abnormal_count": abnormal_count,
        "overall_recommendations": overall_recommendations,
        "summary": f"Analyzed {total_tests} medical tests. Health Score: {health_score}/100. {abnormal_count} results need attention." + (f" {len(condition_details)} potential health conditions identified." if condition_details else ""),
        "urgent_care_needed": any(analysis["status"] in ["HIGH", "LOW"] and analysis["value"] > analysis.get("critical_threshold", float('inf')) for analysis in individual_analyses)
    }

@app.route('/')
def index():
    return render_template('medical_simplifier.html')

@app.route('/simplify', methods=['POST'])
def simplify_medical_report():
    """
    Main endpoint for medical report simplification
    HACKATHON COMPLIANT - No AI models, pure rule-based processing
    """
    try:
        data = request.get_json()

        if not data or 'medical_text' not in data:
            return jsonify({
                "error": "No medical report text provided",
                "success": False
            })

        medical_text = data['medical_text'].strip()

        if not medical_text:
            return jsonify({
                "error": "Empty medical report text",
                "success": False
            })

        # Process using rule-based extraction
        extracted_data = extract_medical_values_comprehensive(medical_text)

        # Generate comprehensive analysis
        health_report = generate_comprehensive_health_report(extracted_data)

        return jsonify({
            "success": True,
            "report": health_report,
            "processing_method": "Rule-based Medical Analysis (HACKATHON COMPLIANT)",
            "sdg_alignment": {
                "sdg_3": "Good Health and Well-being - Making medical information accessible",
                "sdg_10": "Reduced Inequalities - Democratizing healthcare understanding"
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        app.logger.error(f"Simplification error: {str(e)}")
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "success": False
        })

@app.route('/health-guide')
def health_guide():
    """Return comprehensive health guide information"""
    return jsonify({
        "organ_systems": ORGAN_SYSTEMS_GUIDE,
        "disease_conditions": DISEASE_CONDITIONS,
        "supported_tests": {
            test_key: {
                "name": test_data["displayName"],
                "category": test_data["category"],
                "what_it_measures": test_data["simple_explanation"]["what_it_is"]
            }
            for test_key, test_data in MEDICAL_KNOWLEDGE_DATABASE.items()
        }
    })

@app.route('/emergency-guide')
def emergency_guide():
    """Emergency symptoms and when to seek immediate care"""
    emergency_info = {
        "immediate_911": [
            "Chest pain or pressure",
            "Difficulty breathing or shortness of breath",
            "Signs of stroke (face drooping, arm weakness, speech difficulty)",
            "Severe allergic reaction",
            "Loss of consciousness",
            "Severe bleeding that won't stop"
        ],
        "urgent_care_needed": [
            "High fever (over 103°F/39.4°C)",
            "Severe abdominal pain",
            "Blood in urine or stool",
            "Yellowing of skin or eyes (jaundice)",
            "Severe headache with vision changes",
            "Persistent vomiting"
        ],
        "see_doctor_soon": [
            "Persistent fatigue lasting weeks",
            "Unexplained weight loss or gain",
            "Changes in bathroom habits",
            "Skin changes or new moles",
            "Persistent cough",
            "Mood changes lasting weeks"
        ]
    }

    return jsonify(emergency_info)

if __name__ == "__main__":
    print("🏥 MEDICAL REPORT SIMPLIFIER - HACKATHON COMPLIANT")
    print("📋 SDG 3: Good Health and Well-being")
    print("📋 SDG 10: Reduced Inequalities")
    print("🚀 Built from scratch with comprehensive health guidance")
    app.run(debug=True, host='0.0.0.0', port=5000)
