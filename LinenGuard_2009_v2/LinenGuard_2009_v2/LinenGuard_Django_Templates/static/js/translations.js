// LINENGUARD - Comprehensive Multi-Lingual Translation Engine (English, Hindi, Telugu)
// Indian Railways Official Linen Traceability & Chain-of-Custody System
// Supports full real-time bidirectional DOM translation with dynamic MutationObserver

const LinenDict = {
  hi: {
    // Brand & System Header
    "LinenGuard": "लिननगार्ड",
    "Indian Railways": "भारतीय रेल",
    "Indian Railways · Linen Operations": "भारतीय रेल · लिनन संचालन",
    "Linen Operations": "लिनन संचालन",
    "Supervisor Console · Control Deck": "पर्यवेक्षक कंसोल · नियंत्रण डेक",
    "Supervisor Console": "पर्यवेक्षक कंसोल",
    "Working offline — will sync": "ऑफ़लाइन कार्य कर रहा है — सिंक होगा",
    "Connected": "कनेक्टेड (ऑनलाइन)",
    "Systems Operational": "प्रणालियाँ सुचारू रूप से कार्यरत",
    "Terminal Checkpoint Hub v4.2": "टर्मिनल चेकपॉइंट हब v4.2",
    "Sign out": "साइन आउट",
    "Sign In": "साइन इन",
    "Sign in": "साइन इन करें",
    "Logout": "लॉग आउट",
    "Staff": "स्टाफ",
    "LinenGuard Traceability Platform": "लिननगार्ड ट्रैसेबिलिटी प्लेटफॉर्म",
    "Northern & South Central Railway Division": "उत्तर एवं दक्षिण मध्य रेलवे मंडल",

    // Login Screen
    "LinenGuard Portal": "लिननगार्ड पोर्टल",
    "Indian Railways Traceability & Chain-of-Custody System": "भारतीय रेल ट्रैसेबिलिटी एवं कस्टडी प्रबंधन प्रणाली",
    "Select Access Role": "पहुंच भूमिका चुनें",
    "Attendant": "अटेंडेंट",
    "Laundry": "लॉन्ड्री",
    "Supervisor": "पर्यवेक्षक (Supervisor)",
    "Employee ID / Badge": "कर्मचारी आईडी / बैज",
    "Password": "पासवर्ड",
    "Secured by IRCTC Railway Operations Architecture": "आईआरसीटीसी रेलवे संचालन आर्किटेक्चर द्वारा सुरक्षित",

    // Attendant Coach Assignment
    "Coach Assignment": "कोच आवंटन",
    "TRAIN ASSIGNED": "ट्रेन आवंटित",
    "COACH CONFIRMATION": "कोच पुष्टि",
    "SHIFT INITIATION": "शिफ्ट प्रारंभ",
    "● 1. TRAIN ASSIGNED": "● 1. ट्रेन आवंटित",
    "○ 2. COACH CONFIRMATION": "○ 2. कोच पुष्टि",
    "○ 3. SHIFT INITIATION": "○ 3. शिफ्ट प्रारंभ",
    "Assigned by your supervisor": "आपके पर्यवेक्षक द्वारा आवंटित",
    "Train:": "ट्रेन:",
    "Train": "ट्रेन",
    "Coach": "कोच",
    "Shift": "शिफ्ट",
    "shift": "शिफ्ट",
    "bedsheets handed over": "चादरें सौंपी गईं",
    "bedsheets in depot": "चादरें डिपो में",
    "allocated to coaches": "कोचों को आवंटित",
    "Route:": "मार्ग:",
    "Confirm & start shift": "पुष्टि करें और शिफ्ट शुरू करें",
    "Your coach assignment has been confirmed.": "आपके कोच आवंटन की पुष्टि हो गई है।",

    // Attendant Action Hub
    "Attendant Action Hub": "अटेंडेंट एक्शन हब",
    "Operational Station:": "संचालन स्टेशन:",
    "Station Alert: Secunderabad (~06:20)": "स्टेशन अलर्ट: सिकंदराबाद (~06:20)",
    "Station Alert": "स्टेशन अलर्ट",
    "View": "देखें",
    "Issue Linen": "लिनन जारी करें",
    "Give linen to a boarding passenger": "सवार होने वाले यात्री को लिनन दें",
    "Collect Item": "आइटम एकत्र करें",
    "Take linen back from a deboarding passenger": "उतरने वाले यात्री से लिनन वापस लें",
    "Today's Coach Reconciliation:": "आज का कोच मिलान:",
    "issued": "जारी",
    "collected": "एकत्रित",

    // Station Alert
    "DEBOARDING SHORTLY": "शीघ्र ही उतर रहे हैं",
    "12 passengers deboarding at Secunderabad": "सिकंदराबाद में 12 यात्री उतर रहे हैं",
    "12 passengers deboarding": "12 यात्री उतर रहे हैं",
    "at Secunderabad": "सिकंदराबाद में",
    "Expected arrival ~06:20": "अपेक्षित आगमन ~06:20",
    "Start collecting": "संग्रह शुरू करें",
    "3 passengers boarding": "3 यात्री सवार हो रहे हैं",
    "At the next station — issue linen when ready": "अगले स्टेशन पर — तैयार होने पर लिनन जारी करें",

    // Issue Linen Screen
    "Action Hub": "एक्शन हब",
    "Issue Linen to Passenger": "यात्री को लिनन जारी करें",
    "Coach Passenger Roster": "कोच यात्री रोस्टर",
    "Passenger Roster": "यात्री सूची",
    "Select a boarding passenger below to begin issuance": "जारी करने के लिए नीचे दिए गए बोर्डिंग यात्री को चुनें",
    "Passengers": "यात्री",
    "Passenger": "यात्री",
    "Berth": "बर्थ",
    "Middle Berth": "मध्यम बर्थ",
    "Lower Berth": "निचली बर्थ",
    "Upper Berth": "ऊपरी बर्थ",
    "Side Lower": "साइड लोअर",
    "Side Upper": "साइड अपर",
    "PNR": "पीएनआर",
    "Destination:": "गंतव्य:",
    "Destination": "गंतव्य",
    "Issued": "जारी किया गया",
    "Boarding now": "अभी सवार हो रहे हैं",
    "Not boarded": "सवार नहीं हुए",
    "Step 1: Selected Passenger": "चरण 1: चयनित यात्री",
    "Step 2: Scan Linen QR Code": "चरण 2: लिनन क्यूआर कोड स्कैन करें",
    "Scan Linen QR Code": "लिनन क्यूआर कोड स्कैन करें",
    "Manual": "मैन्युअल",
    "Demo Code": "डेमो कोड",
    "Align physical linen QR code inside target": "टार्गेट के अंदर लिनन का क्यूआर कोड संरेखित करें",
    "Simulate QR Detect:": "क्यूआर सिमुलेट करें:",
    "Enter Linen ID manually": "लिनन आईडी हाथ से दर्ज करें",
    "Verify": "जांचें",
    "Quick Demonstration Scans:": "त्वरित प्रदर्शन स्कैन:",
    "Registered:": "पंजीकृत:",
    "Unregistered:": "अपंजीकृत:",
    "QR Scanned — Manufacturer Tag": "क्यूआर स्कैन हुआ — निर्माता टैग",
    "Inventory Status: Ready in Depot Stock": "इन्वेंटरी स्थिति: डिपो स्टॉक में तैयार",
    "Detected": "सत्यापित",
    "INVENTORY REJECTION: Unregistered Linen Tag": "इन्वेंटरी अस्वीकृति: अपंजीकृत लिनन टैग",
    "This item is not present in depot inventory. Manufacturer items must be registered by Laundry intake before coach issuance.": "यह आइटम डिपो इन्वेंट्री में मौजूद नहीं है। कोच जारी करने से पहले लॉन्ड्री इंटेक द्वारा निर्माता आइटम पंजीकृत होना अनिवार्य है।",
    "Manually check this matches": "पुष्टि करें कि यह मेल खाता है",
    "before assigning.": "आवंटन से पहले।",
    "Assign Linen to Passenger": "यात्री को लिनन सौंपें",
    "Assign": "आवंटित करें",

    // Collect Item Screen
    "Collect Linen Item": "लिनन आइटम एकत्र करें",
    "Collect Soiled Linen Item": "इस्तेमाल किया हुआ लिनन एकत्र करें",
    "Point camera at Linen QR code": "कैमरे को लिनन क्यूआर कोड पर रखें",
    "Hold camera steady 6–10 inches from tag": "कैमरे को टैग से 6-10 इंच दूर स्थिर रखें",
    "Enter linen ID manually": "लिनन आईडी हाथ से दर्ज करें",
    "Demo Scan:": "डेमो स्कैन:",
    "Scanned — Blanket": "स्कैन हुआ — कंबल",
    "Scanned — Bedsheet": "स्कैन हुआ — चादर",
    "Scanned — Towel": "स्कैन हुआ — तौलिया",
    "Scanned — Pillow Cover": "स्कैन हुआ — तकिया कवर",
    "Assigned to Coach": "कोच को सौंपा गया",
    "Verified": "सत्यापित",
    "Confirm": "पुष्टि करें",
    "Coach Inventory Status": "कोच इन्वेंट्री स्थिति",
    "Items Issued": "जारी किए गए आइटम",
    "Items Collected": "एकत्रित किए गए आइटम",
    "End Shift & Sweep Report": "शिफ्ट समाप्त करें और स्वीप रिपोर्ट",

    // End Sweep Report
    "End-of-Coach Sweep Report": "कोच स्वीप समाप्ति रिपोर्ट",
    "Reconciled Coach Totals": "पुनर्मिलान कोच कुल",
    "Expected": "अपेक्षित",
    "Returned": "वापस मिला",
    "Damaged": "क्षतिग्रस्त",
    "Missing": "लापता",
    "Submitting this sweep report closes the active shift collection window and forwards discrepancy records to the depot supervisor console.": "इस स्वीप रिपोर्ट को जमा करने से सक्रिय शिफ्ट विंडो बंद हो जाती है और विसंगति रिकॉर्ड डिपो पर्यवेक्षक कंसोल को भेज दिए जाते हैं।",
    "Submit Sweep Report": "स्वीप रिपोर्ट सबमिट करें",

    // Laundry Portal
    "Manufacturer Linen Intake": "निर्माता लिनन इंटेक",
    "Depot Intake Hub": "डिपो इंटेक हब",
    "Scan manufacturer-attached QR codes directly into depot inventory": "निर्माता के क्यूआर कोड को सीधे डिपो इन्वेंट्री में स्कैन करें",
    "Intake Scan (Register)": "इंटेक स्कैन (पंजीकरण)",
    "Washing Intake": "धुलाई इंटेक",
    "Scan Manufacturer Tag": "निर्माता टैग स्कैन करें",
    "Factory Affixed": "फ़ैक्टरी संलग्न",
    "Item Category": "वस्तु श्रेणी",
    "Bedsheet": "चादर",
    "Blanket": "कंबल",
    "Towel": "तौलिया",
    "Pillow Cover": "तकिया कवर",
    "Use Camera Scanner": "कैमरा स्कैनर का उपयोग करें",
    "Point camera at manufacturer linen QR code": "कैमरे को निर्माता लिनन क्यूआर कोड पर रखें",
    "Manufacturer Attached QR Code / Barcode": "निर्माता संलग्न क्यूआर कोड / बारकोड",
    "Add": "जोड़ें",
    "Supports physical barcode gun scanner, mobile camera scanner, or manual code entry.": "बारकोड स्कैनर गन, मोबाइल कैमरा स्कैनर, या मैन्युअल कोड प्रविष्टि का समर्थन करता है।",
    "Quick-Scan Sample Factory QR Tags:": "त्वरित स्कैन नमूना फ़ैक्टरी क्यूआर टैग:",
    "Inventory Readiness": "इन्वेंटरी तत्परता",
    "Registered Today": "आज पंजीकृत",
    "In Depot Inventory": "डिपो इन्वेंट्री में",
    "Central Railway Laundry Intake": "मध्य रेल लॉन्ड्री इंटेक",
    "Arrival Verification & Washing Cycle Dispatch": "आगमन सत्यापन एवं धुलाई चक्र प्रेषण",
    "Scan soiled linen QR for laundry intake": "लॉन्ड्री इंटेक के लिए गंदे लिनन का क्यूआर स्कैन करें",
    "Confirms arrival from train terminal sweep": "ट्रेन टर्मिनल स्वीप से आगमन की पुष्टि करता है",
    "Received at laundry": "लॉन्ड्री में प्राप्त",
    "Category: Bedsheet · Inward Terminal Sweep Batch": "श्रेणी: चादर · आवक टर्मिनल स्वीप बैच",
    "Move to washing": "धुलाई के लिए भेजें",
    "Depot Processing Telemetry": "डिपो प्रसंस्करण टेलीमेट्री",

    // Supervisor Console
    "Assign & Hand Off": "आवंटन एवं हैंड-ऑफ",
    "Dashboard": "डैशबोर्ड",
    "Missing Linen & Settlement": "लापता लिनन एवं निपटान",
    "Audit Log": "ऑडिट लॉग",
    "Search": "खोजें",
    "Zone Attendant Roster & Coach Allocation": "ज़ोन अटेंडेंट रोस्टर एवं कोच आवंटन",
    "Zone Attendant / Employee": "ज़ोन अटेंडेंट / कर्मचारी",
    "Allocated Coach": "आवंटित कोच",
    "Decided Shift": "निर्धारित शिफ्ट",
    "Bedsheets Handed Over": "सौंपी गई चादरें",
    "Status": "स्थिति",
    "Action": "कार्रवाई",
    "Save": "सहेजें",
    "Save All Allocations": "सभी आवंटन सहेजें",
    "Ready / Handed Off": "तैयार / सौंप दिया गया",
    "Assigned": "आवंटित",
    "Pending Confirmation": "पुष्टि लंबित",
    "Operations Command Dashboard": "संचालन कमान डैशबोर्ड",
    "Real-time Depot & Coach Traceability Telemetry": "रीयल-टाइम डिपो और कोच ट्रैसेबिलिटी टेलीमेट्री",
    "Live operational cycle": "सक्रिय संचालन चक्र",
    "Total Linen": "कुल लिनन",
    "Unaccounted": "लापता / अनअकाउंटेड",
    "Sync conflicts": "सिंक विसंगतियाँ",
    "Unaccounted Items": "लापता / अनअकाउंटेड वस्तुएं",
    "No unaccounted items.": "कोई लापता वस्तु नहीं।",
    "Category:": "श्रेणी:",
    "Current Status:": "वर्तमान स्थिति:",
    "Last Checkpoint:": "अंतिम चेकपॉइंट:",
    "Decision / Settlement Action": "निर्णय / निपटान कार्रवाई",
    "Mark as Lost": "खोया हुआ चिह्नित करें",
    "Mark as Recovered": "पुनर्प्राप्त चिह्नित करें",
    "Waive Off": "माफ़ करें",
    "Audit Trail": "ऑडिट ट्रेल",
    "Operational Audit Trail": "संचालन ऑडिट ट्रेल",
    "Global Traceability Search": "वैश्विक ट्रैसेबिलिटी खोज",
    "Executive Dashboard": "कार्यकारी डैशबोर्ड",
    "Linen Management": "लिनन प्रबंधन",
    "Register Linen": "नया लिनन पंजीकृत करें",
    "All Linen Inventory": "संपूर्ण लिनन सूची",
    "Journey Assignments": "यात्रा आवंटन",
    "Assign Linen": "लिनन आवंटित करें",
    "Active Assignments": "सक्रिय आवंटन",
    "Train Attender Station": "ट्रेन अटेंडेंट स्टेशन",
    "Collection Dashboard": "संग्रह डैशबोर्ड",
    "Collection History": "संग्रह इतिहास",
    "Laundry Processing": "लॉन्ड्री प्रक्रिया",
    "Laundry Station": "लॉन्ड्री स्टेशन",
    "Intake Scanner": "इनटेक स्कैनर",
    "Washing & Reissue": "धुलाई और पुनः जारी",
    "Intelligence & Reports": "खुफिया और रिपोर्ट",
    "Unaccounted Linen": "लापता लिनन",
    "Train Analytics": "ट्रेन विश्लेषण",
    "Coach Hotspots": "कोच नुकसान हॉटस्पॉट",
    "Morning": "सुबह (Morning)",
    "Evening": "शाम (Evening)",
    "Night": "रात (Night)"
  },

  te: {
    // Brand & System Header
    "LinenGuard": "లినెన్‌గార్డ్",
    "Indian Railways": "భారతీయ రైల్వేలు",
    "Indian Railways · Linen Operations": "భారతీయ రైల్వేలు · లినెన్ కార్యకలాపాలు",
    "Linen Operations": "లినెన్ కార్యకలాపాలు",
    "Supervisor Console · Control Deck": "సూపర్‌వైజర్ కన్సోల్ · కంట్రోల్ డెక్",
    "Supervisor Console": "సూపర్‌వైజర్ కన్సోల్",
    "Working offline — will sync": "ఆఫ్‌లైన్‌లో ఉంది — సింక్ అవుతుంది",
    "Connected": "కనెక్ట్ చేయబడింది",
    "Systems Operational": "సిస్టమ్స్ సాధారణంగా పనిచేస్తున్నాయి",
    "Terminal Checkpoint Hub v4.2": "టెర్మినల్ చెక్‌పాయింట్ హబ్ v4.2",
    "Sign out": "సైన్ అవుట్",
    "Sign In": "సైన్ ఇన్",
    "Sign in": "సైన్ ఇన్ చేయండి",
    "Logout": "లాగ్ అవుట్",
    "Staff": "సిబ్బంది",
    "LinenGuard Traceability Platform": "లినెన్‌గార్డ్ ట్రేసిబిలిటీ ప్లాట్‌ఫారమ్",
    "Northern & South Central Railway Division": "ఉత్తర మరియు దక్షిణ మధ్య రైల్వే డివిజన్",

    // Login Screen
    "LinenGuard Portal": "లినెన్‌గార్డ్ పోర్టల్",
    "Indian Railways Traceability & Chain-of-Custody System": "భారతీయ రైల్వేల ట్రేసిబిలిటీ & కస్టడీ నిర్వహణ వ్యవస్థ",
    "Select Access Role": "యాక్సెస్ పాత్రను ఎంచుకోండి",
    "Attendant": "అటెండర్",
    "Laundry": "లాండ్రీ",
    "Supervisor": "సూపర్‌వైజర్ (Supervisor)",
    "Employee ID / Badge": "ఉద్యోగి ID / బ్యాడ్జ్",
    "Password": "పాస్‌వర్డ్",
    "Secured by IRCTC Railway Operations Architecture": "IRCTC రైల్వే కార్యకలాపాల ద్వారా రక్షించబడింది",

    // Attendant Coach Assignment
    "Coach Assignment": "కోచ్ కేటాయింపు",
    "TRAIN ASSIGNED": "రైలు కేటాయించబడింది",
    "COACH CONFIRMATION": "కోచ్ ధృవీకరణ",
    "SHIFT INITIATION": "షిఫ్ట్ ప్రారంభం",
    "● 1. TRAIN ASSIGNED": "● 1. రైలు కేటాయించబడింది",
    "○ 2. COACH CONFIRMATION": "○ 2. కోచ్ ధృవీకరణ",
    "○ 3. SHIFT INITIATION": "○ 3. షిఫ్ట్ ప్రారంభం",
    "Assigned by your supervisor": "మీ సూపర్‌వైజర్ ద్వారా కేటాయించబడింది",
    "Train:": "రైలు:",
    "Train": "రైలు",
    "Coach": "కోచ్",
    "Shift": "షిఫ్ట్",
    "shift": "షిఫ్ట్",
    "bedsheets handed over": "బెడ్‌షీట్లు అప్పగించబడ్డాయి",
    "bedsheets in depot": "బెడ్‌షీట్లు డిపోలో ఉన్నాయి",
    "allocated to coaches": "కోచ్‌లకు కేటాయించబడ్డాయి",
    "Route:": "మార్గం:",
    "Confirm & start shift": "ధృవీకరించి షిఫ్ట్ ప్రారంభించండి",
    "Your coach assignment has been confirmed.": "మీ కోచ్ కేటాయింపు ధృవీకరించబడింది.",

    // Attendant Action Hub
    "Attendant Action Hub": "అటెండర్ యాక్షన్ హబ్",
    "Operational Station:": "ఆపరేషనల్ స్టేషన్:",
    "Station Alert: Secunderabad (~06:20)": "స్టేషన్ అలర్ట్: సికింద్రాబాద్ (~06:20)",
    "Station Alert": "స్టేషన్ అలర్ట్",
    "View": "చూడండి",
    "Issue Linen": "లినెన్ జారీ చేయండి",
    "Give linen to a boarding passenger": "ఎక్కే ప్రయాణికుడికి లినెన్ ఇవ్వండి",
    "Collect Item": "వస్తువును సేకరించండి",
    "Take linen back from a deboarding passenger": "దిగే ప్రయాణికుడి నుండి లినెన్ తిరిగి తీసుకోండి",
    "Today's Coach Reconciliation:": "నేటి కోచ్ రీకన్సిలియేషన్:",
    "issued": "జారీ చేసినవి",
    "collected": "సేకరించినవి",

    // Station Alert
    "DEBOARDING SHORTLY": "త్వరలో దిగనున్నారు",
    "12 passengers deboarding at Secunderabad": "సికింద్రాబాద్‌లో 12 మంది ప్రయాణికులు దిగుతున్నారు",
    "12 passengers deboarding": "12 మంది ప్రయాణికులు దిగుతున్నారు",
    "at Secunderabad": "సికింద్రాబాద్‌లో",
    "Expected arrival ~06:20": "అంచనా రాక ~06:20",
    "Start collecting": "సేకరణ ప్రారంభించండి",
    "3 passengers boarding": "3 ప్రయాణికులు ఎక్కుతున్నారు",
    "At the next station — issue linen when ready": "తదుపరి స్టేషన్‌లో — సిద్ధంగా ఉన్నప్పుడు లినెన్ ఇవ్వండి",

    // Issue Linen Screen
    "Action Hub": "యాక్షన్ హబ్",
    "Issue Linen to Passenger": "ప్రయాణికుడికి లినెన్ జారీ చేయండి",
    "Coach Passenger Roster": "కోచ్ ప్రయాణికుల జాబితా",
    "Passenger Roster": "ప్రయాణికుల జాబితా",
    "Select a boarding passenger below to begin issuance": "జారీ ప్రారంభించడానికి క్రింది ప్రయాణికుడిని ఎంచుకోండి",
    "Passengers": "ప్రయాణికులు",
    "Passenger": "ప్రయాణికుడు",
    "Berth": "బెర్త్",
    "Middle Berth": "మిడిల్ బెర్త్",
    "Lower Berth": "లోయర్ బెర్త్",
    "Upper Berth": "అప్పర్ బెర్త్",
    "Side Lower": "సైడ్ లోయర్",
    "Side Upper": "సైడ్ అప్పర్",
    "PNR": "PNR",
    "Destination:": "గమ్యస్థానం:",
    "Destination": "గమ్యస్థానం",
    "Issued": "జారీ చేయబడింది",
    "Boarding now": "ఇప్పుడే ఎక్కుతున్నారు",
    "Not boarded": "ఎక్కలేదు",
    "Step 1: Selected Passenger": "దశ 1: ఎంచుకున్న ప్రయాణికుడు",
    "Step 2: Scan Linen QR Code": "దశ 2: లినెన్ QR కోడ్‌ను స్కాన్ చేయండి",
    "Scan Linen QR Code": "లినెన్ QR కోడ్‌ను స్కాన్ చేయండి",
    "Manual": "మాన్యువల్",
    "Demo Code": "డెమో కోడ్",
    "Align physical linen QR code inside target": "టార్గెట్ లోపల లినెన్ QR కోడ్‌ను ఉంచండి",
    "Simulate QR Detect:": "QR డిటెక్ట్ అనుకరించండి:",
    "Enter Linen ID manually": "లినెన్ ID మాన్యువల్‌గా నమోదు చేయండి",
    "Verify": "ధృవీకరించు",
    "Quick Demonstration Scans:": "శీఘ్ర ప్రదర్శన స్కాన్లు:",
    "Registered:": "నమోదైనవి:",
    "Unregistered:": "నమోదుకానివి:",
    "QR Scanned — Manufacturer Tag": "QR స్కాన్ చేయబడింది — తయారీదారు ట్యాగ్",
    "Inventory Status: Ready in Depot Stock": "నిల్వ స్థితి: డిపో స్టాక్‌లో సిద్ధంగా ఉంది",
    "Detected": "గుర్తించబడింది",
    "INVENTORY REJECTION: Unregistered Linen Tag": "ఇన్వెంటరీ తిరస్కరణ: నమోదుకాని లినెన్ ట్యాగ్",
    "This item is not present in depot inventory. Manufacturer items must be registered by Laundry intake before coach issuance.": "ఈ వస్తువు డిపో నిల్వలో లేదు. కోచ్ జారీకి ముందు లాండ్రీ ఇన్‌టేక్ ద్వారా తయారీదారు వస్తువులను నమోదు చేయాలి.",
    "Manually check this matches": "ఇది సరిపోలుతుందని మాన్యువల్‌గా తనిఖీ చేయండి",
    "before assigning.": "కేటాయించే ముందు.",
    "Assign Linen to Passenger": "ప్రయాణికుడికి లినెన్ కేటాయించండి",
    "Assign": "కేటాయించు",

    // Collect Item Screen
    "Collect Linen Item": "లినెన్ వస్తువును సేకరించండి",
    "Collect Soiled Linen Item": "వాడిన లినెన్ వస్తువును సేకరించండి",
    "Point camera at Linen QR code": "కెమెరాను లినెన్ QR కోడ్ వైపు ఉంచండి",
    "Hold camera steady 6–10 inches from tag": "కెమెరాను ట్యాగ్‌కు 6-10 అంగుళాల దూరంలో స్థిరంగా ఉంచండి",
    "Enter linen ID manually": "లినెన్ ID మాన్యువల్‌గా నమోదు చేయండి",
    "Demo Scan:": "డెమో స్కాన్:",
    "Scanned — Blanket": "స్కాన్ చేయబడింది — దుప్పటి",
    "Scanned — Bedsheet": "స్కాన్ చేయబడింది — బెడ్‌షీట్",
    "Scanned — Towel": "స్కాన్ చేయబడింది — టవల్",
    "Scanned — Pillow Cover": "స్కాన్ చేయబడింది — దిండు కవర్",
    "Assigned to Coach": "కోచ్‌కు కేటాయించబడింది",
    "Verified": "ధృవీకరించబడింది",
    "Confirm": "ధృవీకరించు",
    "Coach Inventory Status": "కోచ్ నిల్వ స్థితి",
    "Items Issued": "జారీ చేసిన వస్తువులు",
    "Items Collected": "సేకరించిన వస్తువులు",
    "End Shift & Sweep Report": "షిఫ్ట్ ముగించు & స్వీప్ నివేదిక",

    // End Sweep Report
    "End-of-Coach Sweep Report": "కోచ్ స్వీప్ ముగింపు నివేదిక",
    "Reconciled Coach Totals": "సరిపోల్చిన కోచ్ మొత్తం",
    "Expected": "ఆశించినవి",
    "Returned": "తిరిగి వచ్చినవి",
    "Damaged": "దెబ్బతిన్నవి",
    "Missing": "తప్పిపోయినవి",
    "Submitting this sweep report closes the active shift collection window and forwards discrepancy records to the depot supervisor console.": "ఈ స్వీప్ నివేదికను సమర్పించడం ద్వారా యాక్టివ్ షిఫ్ట్ ముగుస్తుంది మరియు వ్యత్యాసాల రికార్డులు డిపో సూపర్‌వైజర్ కన్సోల్‌కు పంపబడతాయి.",
    "Submit Sweep Report": "స్వీప్ నివేదికను సమర్పించండి",

    // Laundry Portal
    "Manufacturer Linen Intake": "తయారీదారు లినెన్ ఇన్‌టేక్",
    "Depot Intake Hub": "డిపో ఇన్‌టేక్ హబ్",
    "Scan manufacturer-attached QR codes directly into depot inventory": "తయారీదారు QR కోడ్‌లను నేరుగా డిపో నిల్వలోకి స్కాన్ చేయండి",
    "Intake Scan (Register)": "ఇన్‌టేక్ స్కాన్ (నమోదు)",
    "Washing Intake": "వాషింగ్ ఇన్‌టేక్",
    "Scan Manufacturer Tag": "తయారీదారు ట్యాగ్ స్కాన్ చేయండి",
    "Factory Affixed": "ఫ్యాక్టరీ ద్వారా అతికించబడింది",
    "Item Category": "వస్తువు వర్గం",
    "Bedsheet": "బెడ్‌షీట్",
    "Blanket": "దుప్పటి",
    "Towel": "టవల్",
    "Pillow Cover": "దిండు కవర్",
    "Use Camera Scanner": "కెమెరా స్కానర్ ఉపయోగించండి",
    "Point camera at manufacturer linen QR code": "కెమెరాను తయారీదారు లినెన్ QR కోడ్ వైపు ఉంచండి",
    "Manufacturer Attached QR Code / Barcode": "తయారీదారు అతికించిన QR కోడ్ / బార్‌కోడ్",
    "Add": "జోడించు",
    "Supports physical barcode gun scanner, mobile camera scanner, or manual code entry.": "ఫిజికల్ బార్‌కోడ్ స్కానర్ గన్, మొబైల్ కెమెరా స్కానర్ లేదా మాన్యువల్ కోడ్ ఎంట్రీకి మద్దతు ఇస్తుంది.",
    "Quick-Scan Sample Factory QR Tags:": "త్వరిత స్కాన్ నమూనా ఫ్యాక్టరీ QR ట్యాగ్‌లు:",
    "Inventory Readiness": "నిల్వ సంసిద్ధత",
    "Registered Today": "నేడు నమోదైనవి",
    "In Depot Inventory": "డిపో నిల్వలో ఉన్నవి",
    "Central Railway Laundry Intake": "సెంట్రల్ రైల్వే లాండ్రీ ఇన్‌టేక్",
    "Arrival Verification & Washing Cycle Dispatch": "రాక ధృవీకరణ & వాషింగ్ సైకిల్ డిస్పాచ్",
    "Scan soiled linen QR for laundry intake": "లాండ్రీ ఇన్‌టేక్ కోసం వాడిన లినెన్ QR స్కాన్ చేయండి",
    "Confirms arrival from train terminal sweep": "రైలు టెర్మినల్ స్వీప్ నుండి రాకను ధృవీకరిస్తుంది",
    "Received at laundry": "లాండ్రీలో స్వీకరించబడింది",
    "Category: Bedsheet · Inward Terminal Sweep Batch": "వర్గం: బెడ్‌షీట్ · టెర్మినల్ స్వీప్ బ్యాచ్",
    "Move to washing": "వాషింగ్‌కు తరలించండి",
    "Depot Processing Telemetry": "డిపో ప్రాసెసింగ్ టెలిమెట్రీ",

    // Supervisor Console
    "Assign & Hand Off": "కేటాయింపు & హ్యాండ్-ఆఫ్",
    "Dashboard": "డాష్‌బోర్డ్",
    "Missing Linen & Settlement": "తప్పిపోయిన లినెన్ & పరిష్కారం",
    "Audit Log": "ఆడిట్ లాగ్",
    "Search": "శోధించండి",
    "Zone Attendant Roster & Coach Allocation": "జోన్ అటెండర్ జాబితా & కోచ్ కేటాయింపు",
    "Zone Attendant / Employee": "జోన్ అటెండర్ / ఉద్యోగి",
    "Allocated Coach": "కేటాయించిన కోచ్",
    "Decided Shift": "నిర్ణయించిన షిఫ్ట్",
    "Bedsheets Handed Over": "అప్పగించిన బెడ్‌షీట్లు",
    "Status": "స్థితి",
    "Action": "చర్య",
    "Save": "సేవ్ చేయండి",
    "Save All Allocations": "అన్ని కేటాయింపులను సేవ్ చేయండి",
    "Ready / Handed Off": "సిద్ధం / అప్పగించబడింది",
    "Assigned": "కేటాయించబడింది",
    "Pending Confirmation": "ధృవీకరణ పెండింగ్‌లో ఉంది",
    "Operations Command Dashboard": "ఆపరేషన్స్ కమాండ్ డాష్‌బోర్డ్",
    "Real-time Depot & Coach Traceability Telemetry": "రియల్ టైమ్ డిపో & కోచ్ ట్రేసిబిలిటీ టెలిమెట్రీ",
    "Live operational cycle": "లైవ్ ఆపరేషనల్ సైకిల్",
    "Total Linen": "మొత్తం లినెన్",
    "Unaccounted": "లెక్కించబడనివి",
    "Sync conflicts": "సింక్ వైరుధ్యాలు",
    "Unaccounted Items": "లెక్కించబడని వస్తువులు",
    "No unaccounted items.": "లెక్కించబడని వస్తువులు లేవు.",
    "Category:": "వర్గం:",
    "Current Status:": "ప్రస్తుత స్థితి:",
    "Last Checkpoint:": "చివరి చెక్‌పాయింట్:",
    "Decision / Settlement Action": "తీర్పు / పరిష్కార చర్య",
    "Mark as Lost": "పోయినట్లు గుర్తించండి",
    "Mark as Recovered": "తిరిగి పొందినట్లు గుర్తించండి",
    "Waive Off": "రద్దు చేయండి",
    "Audit Trail": "ఆడిట్ రికార్డు",
    "Operational Audit Trail": "ఆపరేషనల్ ఆడిట్ ట్రయిల్",
    "Global Traceability Search": "గ్లోబల్ ట్రేసిబిలిటీ సెర్చ్",
    "Executive Dashboard": "ఎగ్జిక్యూటివ్ డాష్‌బోర్డ్",
    "Linen Management": "లినెన్ నిర్వహణ",
    "Register Linen": "కొత్త లినెన్ నమోదు",
    "All Linen Inventory": "మొత్తం లినెన్ నిల్వ",
    "Journey Assignments": "ప్రయాణ కేటాయింపులు",
    "Assign Linen": "లినెన్ కేటాయించండి",
    "Active Assignments": "యాక్టివ్ కేటాయింపులు",
    "Train Attender Station": "రైలు అటెండర్ స్టేషన్",
    "Collection Dashboard": "కలెక్షన్ డాష్‌బోర్డ్",
    "Collection History": "కలెక్షన్ చరిత్ర",
    "Laundry Processing": "లాండ్రీ ప్రాసెసింగ్",
    "Laundry Station": "లాండ్రీ స్టేషన్",
    "Intake Scanner": "ఇన్‌టేక్ స్కానర్",
    "Washing & Reissue": "వాషింగ్ & రీ-ఇష్యూ",
    "Intelligence & Reports": "ఇంటెలిజెన్స్ & నివేదికలు",
    "Unaccounted Linen": "తప్పిపోయిన లినెన్",
    "Train Analytics": "రైలు విశ్లేషణ",
    "Coach Hotspots": "కోచ్ నష్టాల హాట్‌స్పాట్‌లు",
    "Morning": "ఉదయం (Morning)",
    "Evening": "సాయంత్రం (Evening)",
    "Night": "రాత్రి (Night)"
  }
};

// Current Language Management
let currentLanguage = localStorage.getItem('linenguard_lang') || 'en';
let isTranslating = false;

// Precompute phrases sorted by length (descending) so multi-word phrases match first
const sortedKeysHi = Object.keys(LinenDict.hi).sort((a, b) => b.length - a.length);
const sortedKeysTe = Object.keys(LinenDict.te).sort((a, b) => b.length - a.length);

function setLanguage(lang) {
  if (lang !== 'en' && lang !== 'hi' && lang !== 'te') lang = 'en';
  currentLanguage = lang;
  
  try {
    localStorage.setItem('linenguard_lang', lang);
    document.cookie = `linenguard_lang=${lang};path=/;max-age=31536000;SameSite=Lax`;
  } catch (e) {}

  updateButtonsUI(lang);
  applyTranslations();

  // Voice confirmation for staff
  if (lang === 'hi') {
    speakText("भाषा बदलकर हिन्दी कर दी गई है।", 'hi-IN');
  } else if (lang === 'te') {
    speakText("భాష తెలుగుకు మార్చబడింది.", 'te-IN');
  }
}

// Alias for onclick handler in HTML
function selectLang(lang) {
  setLanguage(lang);
}

function updateButtonsUI(lang) {
  if (typeof document === 'undefined') return;
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  document.querySelectorAll(`#lang-${lang}, .lang-btn[data-lang="${lang}"]`).forEach(btn => {
    btn.classList.add('active');
  });

  const labelEl = document.getElementById('current-lang-label');
  if (labelEl) {
    if (lang === 'hi') labelEl.innerHTML = '🇮🇳 हिन्दी (Hindi)';
    else if (lang === 'te') labelEl.innerHTML = '🇮🇳 తెలుగు (Telugu)';
    else labelEl.innerHTML = '🇬🇧 English';
  }
}

function t(key, fallback = "") {
  if (currentLanguage === 'en') return key || fallback;
  const dict = LinenDict[currentLanguage] || {};
  return dict[key] || fallback || key;
}

function translateString(str, lang) {
  if (!str || typeof str !== 'string' || lang === 'en') return str;
  const dict = LinenDict[lang] || {};

  const trimmed = str.trim();
  // Exact match
  if (dict[trimmed]) {
    return str.replace(trimmed, dict[trimmed]);
  }

  // Regex rules for dynamic railway data
  let res = str;

  if (lang === 'hi') {
    res = res
      .replace(/\bTrain\s+(\d+)/gi, 'ट्रेन $1')
      .replace(/\bCoach\s+([A-Za-z0-9]+)/gi, 'कोच $1')
      .replace(/\bBerth\s+(\d+)/gi, 'बर्थ $1')
      .replace(/(\d+)\s+bedsheets/gi, '$1 चादरें')
      .replace(/(\d+)\s+passengers\s+deboarding/gi, '$1 यात्री उतर रहे हैं')
      .replace(/(\d+)\s+passengers\s+boarding/gi, '$1 यात्री सवार हो रहे हैं')
      .replace(/(\d+)\s+Passengers/gi, '$1 यात्री')
      .replace(/(\d+)\s+passengers/gi, '$1 यात्री')
      .replace(/(\d+)\s+issued/gi, '$1 जारी')
      .replace(/(\d+)\s+collected/gi, '$1 एकत्रित')
      .replace(/Destination:\s*(.*)/gi, 'गंतव्य: $1')
      .replace(/Route:\s*(.*)/gi, 'मार्ग: $1')
      .replace(/Passenger:\s*(.*)/gi, 'यात्री: $1');
  } else if (lang === 'te') {
    res = res
      .replace(/\bTrain\s+(\d+)/gi, 'రైలు $1')
      .replace(/\bCoach\s+([A-Za-z0-9]+)/gi, 'కోచ్ $1')
      .replace(/\bBerth\s+(\d+)/gi, 'బెర్త్ $1')
      .replace(/(\d+)\s+bedsheets/gi, '$1 బెడ్‌షీట్లు')
      .replace(/(\d+)\s+passengers\s+deboarding/gi, '$1 ప్రయాణికులు దిగుతున్నారు')
      .replace(/(\d+)\s+passengers\s+boarding/gi, '$1 ప్రయాణికులు ఎక్కుతున్నారు')
      .replace(/(\d+)\s+Passengers/gi, '$1 ప్రయాణికులు')
      .replace(/(\d+)\s+passengers/gi, '$1 ప్రయాణికులు')
      .replace(/(\d+)\s+issued/gi, '$1 జారీ చేసినవి')
      .replace(/(\d+)\s+collected/gi, '$1 సేకరించినవి')
      .replace(/Destination:\s*(.*)/gi, 'గమ్యస్థానం: $1')
      .replace(/Route:\s*(.*)/gi, 'మార్గం: $1')
      .replace(/Passenger:\s*(.*)/gi, 'ప్రయాణికుడు: $1');
  }

  // Phrase substitution
  const keys = (lang === 'hi') ? sortedKeysHi : sortedKeysTe;
  for (let i = 0; i < keys.length; i++) {
    const k = keys[i];
    if (k.length > 3 && res.includes(k)) {
      res = res.split(k).join(dict[k]);
    }
  }

  return res;
}

function applyTranslations() {
  if (isTranslating || typeof document === 'undefined' || !document.body) return;
  isTranslating = true;

  try {
    const lang = currentLanguage;
    const dict = LinenDict[lang] || {};

    // 1. Explicit data-i18n elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (lang === 'en') {
        if (el._origI18nText !== undefined) el.textContent = el._origI18nText;
      } else {
        if (el._origI18nText === undefined) el._origI18nText = el.textContent;
        if (dict[key]) el.textContent = dict[key];
        else el.textContent = translateString(el._origI18nText, lang);
      }
    });

    // 2. Walk all DOM text nodes
    if (typeof document !== 'undefined' && typeof document.createTreeWalker === 'function' && typeof NodeFilter !== 'undefined' && document.body) {
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
      {
        acceptNode: function(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          const tag = parent.tagName.toUpperCase();
          if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return NodeFilter.FILTER_REJECT;
          if (parent.classList.contains('font-mono') && !parent.classList.contains('translate-mono')) {
            // Keep codes, PNRs, numbers intact unless explicit
            const txt = node.nodeValue.trim();
            if (/^[A-Z0-9\-\•\.\/]+$/.test(txt)) return NodeFilter.FILTER_REJECT;
          }
          if (parent.classList.contains('lang-btn')) return NodeFilter.FILTER_REJECT;
          if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    let node;
    while ((node = walker.nextNode())) {
      if (node._origText === undefined) {
        node._origText = node.nodeValue;
      }

      if (lang === 'en') {
        if (node.nodeValue !== node._origText) {
          node.nodeValue = node._origText;
        }
      } else {
        const translated = translateString(node._origText, lang);
        if (node.nodeValue !== translated) {
          node.nodeValue = translated;
        }
      }
    }
    }

    // 3. Translate form attributes (placeholders, titles, values)
    document.querySelectorAll('input, textarea').forEach(el => {
      if (el.placeholder) {
        if (el._origPlaceholder === undefined) el._origPlaceholder = el.placeholder;
        if (lang === 'en') el.placeholder = el._origPlaceholder;
        else el.placeholder = translateString(el._origPlaceholder, lang);
      }
    });

    document.querySelectorAll('[title]').forEach(el => {
      if (el.title) {
        if (el._origTitle === undefined) el._origTitle = el.title;
        if (lang === 'en') el.title = el._origTitle;
        else el.title = translateString(el._origTitle, lang);
      }
    });

    document.querySelectorAll('input[type="submit"], input[type="button"]').forEach(el => {
      if (el.value) {
        if (el._origValue === undefined) el._origValue = el.value;
        if (lang === 'en') el.value = el._origValue;
        else el.value = translateString(el._origValue, lang);
      }
    });

  } catch (err) {
    console.error("Translation engine error:", err);
  } finally {
    isTranslating = false;
  }
}

// Speech Synthesis Helper
function speakText(text, langCode = 'hi-IN') {
  if (!('speechSynthesis' in window)) return;
  try {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  } catch (e) {}
}

// Debounced reactive observer for DOM mutations
let mutationDebounceTimer = null;
function setupMutationObserver() {
  if (!window.MutationObserver) return;
  const observer = new MutationObserver(mutations => {
    if (isTranslating || currentLanguage === 'en') return;
    let hasRelevantChanges = false;
    for (let i = 0; i < mutations.length; i++) {
      const m = mutations[i];
      if (m.type === 'childList' && (m.addedNodes.length > 0)) {
        hasRelevantChanges = true;
        break;
      }
      if (m.type === 'characterData') {
        hasRelevantChanges = true;
        break;
      }
    }
    if (hasRelevantChanges) {
      clearTimeout(mutationDebounceTimer);
      mutationDebounceTimer = setTimeout(() => {
        applyTranslations();
      }, 50);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true
  });
}

// Initialization on DOM readiness
function initTranslations() {
  const saved = localStorage.getItem('linenguard_lang') || 'en';
  currentLanguage = saved;
  updateButtonsUI(saved);
  applyTranslations();
  setupMutationObserver();
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTranslations);
  } else {
    initTranslations();
  }
}

if (typeof window !== 'undefined') {
  if (typeof window.addEventListener === 'function') {
    window.addEventListener('pageshow', () => {
    const saved = (typeof localStorage !== 'undefined') ? (localStorage.getItem('linenguard_lang') || 'en') : 'en';
    if (saved !== currentLanguage) {
      setLanguage(saved);
    } else {
      updateButtonsUI(saved);
      applyTranslations();
    }
  });
  }

  // Expose globally
  window.setLanguage = setLanguage;
  window.selectLang = selectLang;
  window.applyTranslations = applyTranslations;
  window.translateString = translateString;
  window.LinenDict = LinenDict;
  window.LinenTranslations = LinenDict;
  window.getCurrentLanguage = () => currentLanguage;
}
