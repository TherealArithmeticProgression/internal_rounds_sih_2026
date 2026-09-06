import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      "login_title": "Login with Voice",
      "phone_number": "Phone Number",
      "otp": "OTP",
      "submit": "Submit",
      "listening": "Listening...",
      "start_voice": "Start Voice Input",
      "punjabi_warning": "Warning: Voice recognition in Punjabi may have limited support. Falling back to Hindi/English numbers is recommended.",
      "scan": "Scan Crop",
      "home": "Home",
      "risk": "Risk",
      "settings": "Settings",
      "result": "Result"
    }
  },
  hi: {
    translation: {
      "login_title": "वॉइस के साथ लॉगिन करें",
      "phone_number": "फ़ोन नंबर",
      "otp": "ओटीपी",
      "submit": "जमा करें",
      "listening": "सुन रहा हूँ...",
      "start_voice": "आवाज़ इनपुट शुरू करें",
      "punjabi_warning": "चेतावनी: पंजाबी में वॉइस रिकग्निशन का सपोर्ट सीमित हो सकता है।",
      "scan": "फसल स्कैन",
      "home": "होम",
      "risk": "जोखिम",
      "settings": "सेटिंग्स",
      "result": "परिणाम"
    }
  },
  pa: {
    translation: {
      "login_title": "ਆਵਾਜ਼ ਨਾਲ ਲਾਗਇਨ ਕਰੋ",
      "phone_number": "ਫੋਨ ਨੰਬਰ",
      "otp": "ਓ.ਟੀ.ਪੀ.",
      "submit": "ਜਮ੍ਹਾਂ ਕਰੋ",
      "listening": "ਸੁਣ ਰਿਹਾ ਹੈ...",
      "start_voice": "ਆਵਾਜ਼ ਇਨਪੁਟ ਸ਼ੁਰੂ ਕਰੋ",
      "punjabi_warning": "ਚੇਤਾਵਨੀ: ਪੰਜਾਬੀ ਵਿੱਚ ਆਵਾਜ਼ ਪਛਾਣ ਦੀ ਸਹਾਇਤਾ ਸੀਮਤ ਹੋ ਸਕਦੀ ਹੈ। ਹਿੰਦੀ/ਅੰਗਰੇਜ਼ੀ ਨੰਬਰਾਂ ਦੀ ਵਰਤੋਂ ਕਰਨ ਦੀ ਸਿਫਾਰਸ਼ ਕੀਤੀ ਜਾਂਦੀ ਹੈ।",
      "scan": "ਫਸਲ ਸਕੈਨ",
      "home": "ਹੋਮ",
      "risk": "ਖਤਰਾ",
      "settings": "ਸੈਟਿੰਗਜ਼",
      "result": "ਨਤੀਜਾ"
    }
  },
  bn: {
    translation: {
      "login_title": "ভয়েস দিয়ে লগইন করুন",
      "phone_number": "ফোন নম্বর",
      "otp": "ওটিপি",
      "submit": "জমা দিন",
      "listening": "শুনছি...",
      "start_voice": "ভয়েস ইনপুট শুরু করুন",
      "punjabi_warning": "সতর্কতা: পাঞ্জাবি ভয়েস সাপোর্ট সীমিত হতে পারে।",
      "scan": "ফসল স্ক্যান",
      "home": "হোম",
      "risk": "ঝুঁকি",
      "settings": "সেটিংস",
      "result": "ফলাফল"
    }
  },
  ta: {
    translation: {
      "login_title": "குரல் மூலம் உள்நுழைக",
      "phone_number": "தொலைபேசி எண்",
      "otp": "OTP",
      "submit": "சமர்ப்பி",
      "listening": "கேட்கிறது...",
      "start_voice": "குரல் உள்ளீட்டைத் தொடங்கு",
      "punjabi_warning": "எச்சரிக்கை: பஞ்சாபி குரல் ஆதரவு குறைவாக இருக்கலாம்.",
      "scan": "பயிர் ஸ்கேன்",
      "home": "முகப்பு",
      "risk": "ஆபத்து",
      "settings": "அமைப்புகள்",
      "result": "முடிவு"
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: "en", 
    fallbackLng: "en",
    interpolation: {
      escapeValue: false 
    }
  });

export default i18n;
