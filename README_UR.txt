انسٹی ٹیوٹ لیجر — اپڈیٹڈ مکمل Build Kit
============================================

یہ Build Kit آپ کے دیے ہوئے اصل Institute Ledger Python سورس، اصل Aptos فونٹس، Jameel Noori Nastaleeq فونٹ، شفاف آئیکن اور آپ کی فراہم کردہ سبز اسٹیشنری تصویر استعمال کرتی ہے۔ کسی متبادل فونٹ یا فرضی لاگ اِن تصویر کا اضافہ نہیں کیا گیا۔

اس Build Kit میں شامل اصلاحات
-----------------------------
- سافٹ ویئر کا نام: Institute Ledger
- آئیکن PNG اور ICO میں ہے؛ بیرونی سفید/سرمئی پس منظر شفاف ہے، جبکہ نشان کے اندر کا سفید کتاب/لیجر برقرار ہے۔
- ڈیفالٹ `assets/background_wallpaper.png` تمام صفحات کا مشترکہ fallback Wallpaper ہے؛ Settings میں Dashboard، Students، Teachers، Fees، Timetable، Attendance، Progress، Accounts، Graphs، Reports، Settings، Login، Create Admin اور Teacher صفحات کے لیے الگ تصویر اور transparency محفوظ کی جا سکتی ہے۔ منتخب صفحہ کھلنے پر اس کا Wallpaper پورے page workspace اور شناختی ہیڈر میں استعمال ہوتا ہے۔
- الگ Cover Photo / کور تصویر کا نظام ختم کر دیا گیا ہے؛ پرانی کور تصویر یا Header Pattern اب استعمال نہیں ہوتے۔
- Settings میں مشترکہ Wallpaper بدلنے، شفافیت 0–100% کرنے، Live Preview اور ڈیفالٹ بحال کرنے کے اختیارات ہیں۔ 0% پر تصویر مکمل نمایاں اور 100% پر مکمل مدھم/غائب ہوگی۔
- ہیڈر میں ادارے کا لوگو، نام، سلوگن، LOCAL • OFFLINE شناخت اور موجودہ صارف/Role کی معلومات اپنی سابقہ جگہوں پر برقرار ہیں۔ ہیڈر میں اب الگ کور تصویر نہیں آتی۔
- مرکزی صفحہ نیچے کی طرف اسکرول کرنے پر شناختی ہیڈر تقریباً 220 ملی سیکنڈ کی نرم ٹرانزیشن کے ساتھ اوپر سمٹ کر غائب ہوتا ہے؛ اوپر کی طرف واپس آنے پر اسی جگہ دوبارہ ظاہر ہوتا ہے۔ Navigation اپنی جگہ برقرار رہتی ہے۔
- Light / Day اور Dark / Night modes Settings میں دستیاب ہیں؛ دونوں موڈز database میں محفوظ رہتے ہیں اور اگلی مرتبہ پروگرام کھولنے پر بھی برقرار رہتے ہیں۔ Login screen بھی منتخب theme کے رنگ استعمال کرتی ہے۔
- ہر installer چلانے کے بعد پروگرام کی پہلی launch پر واضح انتخاب آتا ہے: `Create a new institute` یا `Open existing database`۔ New Institute کے انتخاب پر خالی data folder لازمی ہے؛ اس فولڈر میں پہلے سے database ہو تو پروگرام اسے استعمال نہیں کرتا اور دوسرے خالی فولڈر کا کہتا ہے۔ نئے خالی ڈیٹابیس پر Create Admin Account کھلتا ہے۔ Existing Database کے انتخاب پر صارف اپنی پرانی DB/backup خود منتخب کرتا ہے۔ ایک مرتبہ درست انتخاب کے بعد اگلی launches معمول کے مطابق محفوظ DB کھولتی ہیں۔
- Profile/account menu میں صرف Change Password اور Log out ہیں۔ Header کی تخصیص کا اختیار Settings میں ہے؛ یہ اکاؤنٹ مینو میں نہیں دکھایا جاتا۔
- نیویگیشن ٹیبز افقی قطار یا عمودی کالم میں دکھانے کا اختیار ہے۔
- Wallpaper کو پورے صفحے کی ایک بڑی bitmap بنانے کے بجائے محدود اونچائی کے tiles میں بنایا جاتا ہے؛ وہ resized tile صفحات کے درمیان cache سے دوبارہ استعمال ہوتا ہے۔ کیلنڈر کی تاریخ، ہفتہ وار شیڈول اور حاضری کے lookup بھی render کے دوران cache/batch کیے جاتے ہیں۔
- عام بٹن اور نیویگیشن ٹیبز کا بنیادی رنگ یکساں سبز/سفید رکھا گیا ہے؛ حاضری جیسے معنی خیز اسٹیٹس بٹن اپنے الگ معنی خیز رنگ برقرار رکھتے ہیں۔
- ایڈمن اکاؤنٹ بنانے اور دوسری اکاؤنٹ درخواست کے فیلڈز میں Enter دبانے سے اگلا خانہ فوکس ہوتا ہے؛ آخری خانے پر Enter جمع/تخلیق کرتا ہے۔
- طلبہ کے Card View میں ابتدائی طور پر 18 کارڈ دکھتے ہیں؛ اگلے کارڈ صرف Load More دبانے پر database سے 18 کے گروپ میں لائے جاتے ہیں۔ اس سے سینکڑوں پروفائل widgets بیک وقت بنانے کا بوجھ کم ہوتا ہے۔
- موجودہ اکاؤنٹ رکھنے والا صارف پہلی اسکرین سے پرانی ڈیٹابیس منتخب کر سکتا ہے۔
- رپورٹس کی اسکرین اور فارمیٹڈ HTML رپورٹس میں دستیاب ادارہ لوگو دکھایا جاتا ہے؛ موجودہ PDF رسید میں لوگو کی سپورٹ بھی برقرار ہے۔
- PDF دیکھنے کے لیے پروگرام Windows کے ڈیفالٹ PDF ریڈر کو استعمال کر سکتا ہے؛ PyMuPDF کو 32-bit پر source سے compile کرنے کی ضرورت نہیں رکھی گئی۔

فائلیں
------
- Institute_Ledger.py : تازہ سورس فائل
- app_icon.png اور app_icon.ico : آپ کا شفاف آئیکن
- assets/background_wallpaper.png : پورے سافٹ ویئر کا واحد ڈیفالٹ Wallpaper
- assets/fonts/ : آپ کے اصل Aptos TTF فونٹس اور Jameel Noori Nastaleeq Regular.ttf
- BUILD_SINGLE_INSTALLER.bat اور Institute_Ledger_Universal.iss : 32-bit اور 64-bit پروگرام بنا کر ایک installer تیار کرنے کی فائلیں

ایک مشترکہ Windows Installer بنانے کے لیے
-----------------------------------------
اس Windows کمپیوٹر پر یہ چیزیں نصب ہونی چاہئیں:
1) Python 3.15 کا 64-bit ورژن
2) Python 3.15 کا 32-bit ورژن
3) دونوں Python installations میں PyInstaller اور Pillow پہلے سے نصب ہوں (build script خودکار upgrade نہیں کرے گی)
4) Inno Setup 6 یا 7

سرکاری ڈاؤن لوڈ صفحات:
Python: https://www.python.org/downloads/windows/
Inno Setup: https://jrsoftware.org/isdl.php

طریقہ:
1) پوری ZIP کو ایک عام فولڈر میں Extract کریں۔ ZIP کے اندر سے BAT فائل مت چلائیں۔
2) اسی Extract کیے ہوئے فولڈر میں BUILD_SINGLE_INSTALLER.bat پر ڈبل کلک کریں۔
3) اسکرپٹ پہلے موجودہ dependencies چیک کرے گی؛ یہ pip packages کو خودکار طور پر upgrade یا تبدیل نہیں کرے گی۔
4) دونوں architecture کے لیے EXE بنے گی، پھر مشترکہ installer تیار کرنے کی کوشش ہوگی۔
5) کامیابی پر فائل output\Institute_Ledger_Setup.exe میں ہوگی۔

ڈیٹابیس کی حفاظت
----------------
- آپ کی اصل taha_school.db فائل اس Build Kit یا installer میں شامل نہیں ہے۔
- کسی نئی یا تبدیل شدہ EXE کو پہلے database کی COPY کے ساتھ آزمائیں۔
- اپنی واحد اصل D:\TAHA_SCHOOL_DATA\taha_school.db فائل کو حذف، منتقل یا overwrite نہ کریں۔
- پہلے سے موجود ایڈمن اکاؤنٹ کے لیے "Open existing database" اختیار استعمال کرکے اپنی پرانی ڈیٹابیس منتخب کریں۔ اگر نئی خالی ڈیٹابیس منتخب کریں گے تو پرانے ریکارڈ خودبخود اس میں نہیں آئیں گے۔
- موجودہ ریویژن میں public self-registration اور Student login بند ہیں؛ Admin کے ذریعے Teacher login بنایا جاتا ہے۔ پرانے student user records کو حذف نہیں کیا گیا۔
- ڈیٹا فولڈر کا انتخاب انسٹالر مکمل ہونے کے بعد پہلی مرتبہ ایپ چلانے پر ہوتا ہے۔ ہر installer run کے بعد ایک مرتبہ `Create a new institute` یا `Open existing database` کا واضح انتخاب دکھایا جاتا ہے؛ اس کے بعد روزمرہ launches میں محفوظ شدہ database استعمال ہوتی ہے۔

اہم وضاحت
---------
یہ اپڈیٹڈ Build Kit ہے، پہلے سے تیار شدہ installer نہیں۔ آخری Institute_Ledger_Setup.exe آپ کے Windows کمپیوٹر پر build script چلانے کے بعد بنے گی۔ نئی EXE بننے کے بعد ایپ، PDF، ڈیزائن، شفاف آئیکن، اور دونوں Windows architectures کی عملی آزمائش ضروری ہے۔


Release Candidate v14 (2026-10-31) — Page Backgrounds، Light/Dark اور First-Run اصلاحات
--------------------------------------------------------------------------------
- Settings میں ہر مرکزی صفحے، Login اور Create Admin کے لیے الگ Wallpaper اور transparency محفوظ کرنے کے اختیارات شامل کیے؛ جہاں override نہ ہو وہاں shared default wallpaper استعمال ہوتا ہے۔
- Navigation بدلتے وقت page workspace، header اور blended Ttk buttons نئی page background کے مطابق refresh ہوتے ہیں۔
- Light / Day اور Dark / Night mode database میں محفوظ ہوتے ہیں؛ Login screen بھی اسی منتخب theme کے مطابق رنگ لیتی ہے۔
- Profile dropdown سے غلط جگہ موجود `Customize header` شارٹ کٹ ہٹا دیا؛ header customizer صرف Settings میں رہتا ہے۔
- ہر Inno Setup run پر one-time `first_install.flag` لازمی install ہوتا ہے؛ اگلی app launch پر واضح `Create a new institute` یا `Open existing database` انتخاب آتا ہے۔ کامیاب انتخاب کے بعد ایپ marker ختم کرتی ہے، اس لیے روزمرہ launch پر بار بار نہیں پوچھا جاتا۔
- New Institute منتخب کرنے پر پرانی database پہلے سے موجود folder میں خودکار طور پر reuse نہیں ہوتی؛ موجودہ DB/backup کے لیے مخصوص Existing Database اختیار استعمال کرنا ضروری ہے۔
- Student Card View میں پوری table کا `SELECT *` نہیں ہوتا؛ count کے بعد صرف 18 مختصر ریکارڈ فی batch لائے جاتے ہیں۔ اگلے کارڈ بٹن سے آتے ہیں۔
- Button wallpaper texture کو 9 الگ sets سے 2 بنیادی surfaces (normal/active/selected) تک کم کیا؛ پرانے image refs محدود history میں رکھے جاتے ہیں۔
- Settings save کے بعد سابقہ active page دوبارہ کھلتا ہے؛ Light/Dark یا wallpaper change کرنے کے بعد لازماً Dashboard پر واپس نہیں پھینکتا۔
- Python syntax، Tk/Xvfb ماڈیول smoke، page wallpaper/header/button sync، new-install Admin setup اور existing DB collision protection کی جانچ کی گئی۔
- Windows native GUI، x86/x64 executable اور Inno Setup compile ابھی اس ماحول میں نہیں کیے گئے۔


Hotfix v14.2 — Windows Startup Dialog Visibility (2026-10-31)
-------------------------------------------------------------
- درست کیا گیا: پہلی تنصیب کے وقت main Tk root کو withdraw کرنے سے اس کے transient startup chooser بھی Windows پر hidden/withdrawn ہو سکتے تھے؛ Python console کھلی رہتی تھی مگر کوئی Login یا New Admin window نظر نہیں آتی تھی۔
- اب database choice کے دوران ایک 1x1 borderless/transparent mapped Tk owner window رکھا جاتا ہے، تاکہ Welcome/New Institute/Existing Database اور file-picker dialogs سامنے نظر آئیں۔ Database منتخب ہونے کے بعد اصل main window decorations اور opacity بحال ہوتی ہیں۔
- startup میں غیر متوقع Python exception آئے تو traceback `%LOCALAPPDATA%\Institute Ledger\startup_error.log` میں محفوظ ہوگا اور error dialog دکھایا جائے گا۔
- Tk/Xvfb میں root withdrawn نہیں بلکہ mapped/invisible owner؛ transient first-run dialog mapped/visible؛ New Institute کے خالی folder پر SchoolApp کا Create Admin screen؛ اور Existing Database selection کی الگ regression test کی گئی۔
- یہ correction آپ کے screenshot میں نظر آنے والی hidden first-run modal window کے سبب کی بنیاد پر کی گئی ہے۔ Windows native GUI/EXE test ابھی بھی درکار ہے۔


Phase 1 / v15.2 Performance Integration
----------------------------------------
اس ریلیز میں LRU image caches، SearchBox Debouncer، محفوظ AsyncWorker اور Reports کی background SQLite read queries شامل ہیں۔ Login UI اور Phase 1 Header/Scroll Controller برقرار ہیں۔ تفصیل PERFORMANCE_INTEGRATION_UR.txt میں ہے۔
