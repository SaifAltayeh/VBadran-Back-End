"""Replace known outdated default copy without touching custom CMS text."""

STALE_COPY = {
    "Start from a clear block. Training, nutrition, or the full system.": "Choose the gym package that matches where you train.",
    "ابدأ من مرحلة واضحة. تدريب، تغذية، أو النظام الكامل.": "اختر باقة الصالة التي تناسب مكان تدريبك.",
    "Follow the work, log what matters, and keep the check-in honest.": "Follow your assigned workout plan and the exercise videos for your gym.",
    "اتبع العمل، سجّل ما يهم، وأبقِ المتابعة صادقة.": "اتبع خطة التمرين المعيَّنة لك وفيديوهات تمارين صالتك.",
    "The plan changes when your recovery, calendar, or strength changes.": "Keep to the plan written for your package. The videos show how each movement is done.",
    "الخطة تتغيّر عندما يتغيّر التعافي أو الجدول أو القوة.": "التزم بالخطة المكتوبة لباقتك. الفيديوهات توضّح طريقة كل حركة.",
    "Real coach support": "Exercise videos",
    "دعم مدرب حقيقي": "فيديوهات التمارين",
    "Check-ins are read by the coach. Adjustments come from your progress, not a template.": "Each package includes instructional videos for the gym you train at.",
    "المتابعة يقرأها المدرب. التعديل يأتي من تقدّمك لا من قالب.": "كل باقة تتضمن فيديوهات تعليمية للصالة التي تتدرّب فيها.",
    "Train anywhere": "Three gyms",
    "تدرّب في أي مكان": "ثلاث صالات",
    "Online coaching works in a commercial gym, a home setup, or while you travel.": "Packages are written for Spark, Platinum, and Oxygen, with videos that match that gym.",
    "التدريب عن بُعد يعمل في نادي تجاري أو منزل أو أثناء السفر.": "الباقات مكتوبة لسبارك وبلاتينوم وأوكسجين، مع فيديوهات تناسب تلك الصالة.",
    "Nutrition guidance": "Personal workout plan",
    "إرشاد تغذية": "خطة تمارين شخصية",
    "Targets and meal structure that fit your life, with room to adjust.": "After your package is confirmed, a workout plan is assigned to your account.",
    "أهداف وبنية وجبات تناسب حياتك، مع مجال للتعديل.": "بعد تأكيد باقتك تُسند خطة تمارين إلى حسابك.",
    "Adults who want a clear plan and a coach who will adjust it. Beginners, returning athletes, and people already training are all in the right place if they can commit to the block.": "Adults who want a training package, a personal workout plan, and exercise videos for Spark, Platinum, or Oxygen.",
    "للبالغين الذين يريدون خطة واضحة ومدرباً يعدّلها. المبتدئ والعائد ومن يتدرّب أصلاً في المكان الصحيح إن التزم بالمرحلة.": "للبالغين الذين يريدون باقة تدريب، وخطة تمارين شخصية، وفيديوهات تعليمية لسبارك أو بلاتينوم أو أوكسجين.",
    "Yes. The assessment sets the starting point. Exercises, volume, and nutrition targets are scaled to where you are, not to a competition stage.": "Yes. The workout plan is written for your level and the gym you train at.",
    "نعم. التقييم يحدّد نقطة البداية. التمارين والحجم وأهداف التغذية تُقاس على مستواك لا على منصة بطولة.": "نعم. خطة التمرين تُكتب لمستواك وللصالة التي تتدرّب فيها.",
    "A gym helps for the strength work. If you train at home, say so in the assessment and the plan is written for the equipment you have.": "Packages are for Spark, Platinum, and Oxygen. Choose the gym where you train.",
    "النادي يساعد في تمارين القوة. إن تدرّبت في المنزل، اذكر ذلك في التقييم وتُكتب الخطة على أدواتك.": "الباقات لسبارك وبلاتينوم وأوكسجين. اختر الصالة التي تتدرّب فيها.",
    "Nutrition Guidance, Training + Nutrition, Body Transformation, and the Progress, Transform, and Elite packages include it. Training-only options stay focused on the sessions.": "No. Badran offers training packages, personalized workout plans, and exercise videos.",
    "إرشاد التغذية، التدريب + التغذية، تحول الجسم، وباقات Progress وTransform وElite تشملها. خيارات التدريب فقط تبقى على الجلسات.": "لا. يقدّم بدران باقات تدريب، وخطط تمارين شخصية، وفيديوهات تعليمية.",
    "Yes, when the program is online. Tell us what you have available and the sessions will match it.": "Packages are gym-based. Choose Spark, Platinum, or Oxygen.",
    "نعم عندما يكون البرنامج عن بُعد. أخبرنا بما يتوفر لديك وستناسب الجلسات ذلك.": "الباقات مرتبطة بالصالات. اختر سبارك أو بلاتينوم أو أوكسجين.",
    "After payment is confirmed, your account is opened and the program appears in your dashboard: schedule, sessions, and nutrition where included.": "After payment is confirmed, your workout plan and exercise videos appear in your member account.",
    "بعد تأكيد الدفع يُفتح حسابك ويظهر البرنامج في لوحتك: الجدول والجلسات والتغذية إن شُملت.": "بعد تأكيد الدفع تظهر خطة التمرين وفيديوهات التمارين في حسابك.",
    "You train with the plan in your dashboard, watch the movement references, and check in on the agreed day. The next week is adjusted from that check-in.": "You follow the assigned plan and watch the exercise videos for your package.",
    "تتدرّب بالخطة في الواجهة، تشاهد مراجع الحركة، وتتابع في اليوم المتفق عليه. الأسبوع التالي يُعدَّل من تلك المتابعة.": "تتبع الخطة المعيَّنة لك وتشاهد فيديوهات التمارين الخاصة بباقتك.",
    "Packages with coach support and messaging include direct messages inside your account, plus the weekly check-in.": "Contact is through the website contact form, email, or the listed social channels. The member account is for your plan and videos.",
    "الباقات التي تشمل دعم المدرب والرسائل تتضمن رسائل داخل حسابك، إضافة للمتابعة الأسبوعية.": "التواصل عبر نموذج الموقع أو البريد أو قنوات التواصل المعروضة. حساب العضو لخطتك وفيديوهاتك.",
    "The order is confirmed, an account is created if you do not already have one, and the program is assigned. You sign in and start from week one.": "The order stays pending until payment is confirmed. Then your plan and videos are assigned.",
    "يُؤكَّد الطلب، يُنشأ حساب إن لم يكن لديك، ويُسند البرنامج. تسجّل الدخول وتبدأ من الأسبوع الأول.": "يبقى الطلب معلّقاً حتى تأكيد الدفع. بعدها تُسند خطتك وفيديوهاتك.",
    "Do programs include nutrition?": "Does this include nutrition?",
    "هل تشمل البرامج تغذية؟": "هل يشمل هذا تغذية؟",
    "How does online coaching work?": "How do the videos and plan work?",
    "كيف يعمل التدريب عن بُعد؟": "كيف تعمل الفيديوهات والخطة؟",
    "Can I communicate directly with the coach?": "How do I contact Badran?",
    "هل أتواصل مع المدرب مباشرة؟": "كيف أتواصل مع بدران؟",
    "VBADRAN started from a simple problem. People were training hard and still guessing. The sessions changed every week because nothing was written down, and the food had no relationship to the work.": "Badran started from a simple problem. People were training hard without a written plan or clear exercise references.",
    "بدأت VBADRAN من مشكلة بسيطة. الناس يتدرّبون بجِدّ وما زالوا يخمّنون. الجلسات كانت تتغيّر كل أسبوع لأن شيئاً لم يُكتب، والطعام لم يكن له علاقة بالتمرين.": "بدأ بدران من مشكلة بسيطة. الناس يتدرّبون بجِدّ بلا خطة مكتوبة ولا مراجع واضحة للحركة.",
    "The coaching is the correction. A block with a point, sessions you can open and follow, and a review that changes the next week instead of repeating the last one.": "The product is a training package with a personal workout plan and exercise videos for your gym.",
    "التدريب هو التصحيح. مرحلة لها هدف، وجلسات تفتحها وتتبعها، ومراجعة تغيّر الأسبوع التالي بدل تكرار السابق.": "المنتج باقة تدريب مع خطة تمارين شخصية وفيديوهات تعليمية لصاللتك.",
    "Sessions and, where included, nutrition targets for the first block of weeks.": "A workout plan and the exercise videos for your package.",
    "جلسات، وحيث يشمل البرنامج أهداف تغذية لأول مرحلة.": "خطة تمارين وفيديوهات تعليمية لباقتك.",
    "Check-ins decide the adjustment. Not a feeling. Not a new program every Monday.": "Your account holds the assigned plan and the videos for your package.",
    "المتابعة تقرر التعديل. ليس شعوراً. وليس برنامجاً جديداً كل اثنين.": "حسابك يحتفظ بالخطة المعيَّنة وفيديوهات باقتك.",
    "Progress is measured. The plan changes when the data says so.": "Progress is measured.",
    "التقدّم يُقاس. والخطة تتغيّر عندما يقول الرقم ذلك.": "التقدّم يُقاس.",
    "Training, nutrition, transformation, and sport-specific blocks. Each one is written for a week you can actually keep.": "Training packages for Spark, Platinum, and Oxygen, with personal workout plans and exercise videos.",
    "تدريب، تغذية، تحول، وكتل رياضية. كل برنامج مكتوب لأسبوع تستطيع الالتزام به.": "باقات تدريب لسبارك وبلاتينوم وأوكسجين، مع خطط تمارين شخصية وفيديوهات تعليمية.",
    "If the choice is not obvious, talk to the coach.": "If the choice is not obvious, send a message from the contact page.",
    "إن لم يكن الاختيار واضحاً، تحدّث مع المدرب.": "إن لم يكن الاختيار واضحاً، أرسل رسالة من صفحة التواصل.",
    "Start your program": "View packages",
    "ابدأ برنامجك": "عرض الباقات",
    "Talk to the coach": "Contact",
    "تحدث مع المدرب": "تواصل",
    "View all programs": "View packages",
    "كل البرامج": "كل الباقات",
    "VBADRAN is a personal training and online coaching practice. It started from a simple problem: people were training hard and still guessing.": "Badran offers training packages, personal workout plans, and instructional exercise videos.",
    "VBADRAN ممارسة للتدريب الشخصي والتدريب عن بُعد. بدأت من مشكلة بسيطة: الناس يتدرّبون بجِدّ وما زالوا يخمّنون.": "يقدّم بدران باقات تدريب، وخطط تمارين شخصية، وفيديوهات تعليمية للتمارين.",
    "The coaching is the correction. A block with a point, sessions you can open and follow, and a review that changes the next week.": "Each member receives a plan assigned to them, with videos that match their package and gym.",
    "التدريب هو التصحيح. مرحلة لها هدف، وجلسات تفتحها وتتبعها، ومراجعة تغيّر الأسبوع التالي.": "يحصل كل مشترك على خطة مخصّصة له، مع فيديوهات تناسب باقته وصالته.",
    "Choose your program and start building a stronger version of yourself.": "Choose your package and start with a workout plan and exercise videos.",
    "اختر برنامجك وابدأ ببناء نسخة أقوى منك.": "اختر باقتك وابدأ بخطة تمارين وفيديوهات تعليمية.",
    "If the level is not obvious, talk to the coach.": "If the level is not obvious, send a message from the contact page.",
    "إن لم يكن المستوى واضحاً، تحدّث مع المدرب.": "إن لم يكن المستوى واضحاً، أرسل رسالة من صفحة التواصل.",
    "Adjust and progress": "Stay consistent",
    "عدّل وتقدّم": "حافظ على الالتزام",
    "Choose your program": "Choose your package",
    "اختر برنامجك": "اختر باقتك",
}

LIST_STALE = {
    ("Training", "Nutrition", "Full system"): ["Spark", "Platinum", "Oxygen"],
    ("تدريب", "تغذية", "النظام الكامل"): ["سبارك", "بلاتينوم", "أوكسجين"],
    ("Workouts", "Check-ins", "Progress"): ["Workout plan", "Exercise videos", "Progress"],
    ("تمارين", "متابعة", "تقدّم"): ["خطة التمرين", "فيديوهات التمارين", "تقدّم"],
    ("Recovery", "Calendar", "Strength"): ["Plan", "Videos", "Consistency"],
    ("تعافٍ", "جدول", "قوة"): ["خطة", "فيديوهات", "التزام"],
}


def replace_stale_copy(value):
    if isinstance(value, str):
        return STALE_COPY.get(value, value)
    if isinstance(value, list):
        if value and all(isinstance(item, str) for item in value):
            replacement = LIST_STALE.get(tuple(value))
            if replacement is not None:
                return replacement
        return [replace_stale_copy(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_stale_copy(item) for key, item in value.items()}
    return value
