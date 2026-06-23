import React, { useState } from 'react';
import { X, HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';

// Fully translated UI and FAQ Content
const TRANSLATIONS = {
  English: { 
    title: "Help & FAQ", 
    desc: "Common questions about HealthBridge Africa", 
    footer: "⚕️ HealthBridge Africa is not a medical service. Always consult a qualified healthcare provider.",
    faqs: [
      { q: "Is HealthBridge Africa a replacement for a doctor?", a: "No, HealthBridge Africa is a health information and triage tool, not a medical service. It helps you understand symptoms, know when to seek care, and get reliable health information in your language. Always consult a qualified healthcare provider for diagnosis and treatment." },
      { q: "What languages are supported?", a: "HealthBridge Africa supports English, Nigerian Pidgin, Swahili, Oromo, Twi, and Amharic. You can switch languages anytime using the dropdown in the top right of the screen. The AI will respond in whichever language you select." },
      { q: "Is my conversation private?", a: "Your conversations are stored securely and linked only to your device session. No name, email, or personal identity is collected or required. Clearing your browser data will start a fresh session." },
      { q: "How accurate is the information?", a: "Responses are grounded in verified sources including WHO guidelines and country-level health data from Nigeria, Ghana, Ethiopia, and Kenya. The AI does not guess or fabricate answers. If it does not have reliable information on a topic, it will say so and recommend consulting a healthcare professional." },
      { q: "How do I use the voice feature?", a: "Tap the microphone button and speak your health question in your chosen language, then tap stop. HealthBridge will transcribe what you said and respond in text. Tap the Listen button on any response to hear it read back to you." },
      { q: "What should I do in a medical emergency?", a: "If you or someone nearby is experiencing a medical emergency like difficulty breathing, chest pain, heavy bleeding, or loss of consciousness, do not use HealthBridge Africa. Go to the nearest hospital immediately or call your local emergency services." }
    ]
  },
  Pidgin: { 
    title: "Help & FAQ", 
    desc: "Question wey people dey always ask about HealthBridge", 
    footer: "⚕️ HealthBridge Africa no be doctor clinic. Make you always check qualified doctor.",
    faqs: [
      { q: "HealthBridge Africa fit replace doctor?", a: "No, HealthBridge Africa na tool to help you understand your health, e no be hospital. Always check qualified doctor for proper treatment." },
      { q: "Which languages dey available?", a: "We get English, Pidgin, Swahili, Oromo, Twi, and Amharic. You fit change am anytime for top." },
      { q: "My conversation dey private?", a: "Yes, everything wey you tok dey secure and e only tie to your device. We no dey collect your name or email." },
      { q: "How sure the information be?", a: "The answers dey come from verified sources like WHO and country health data. AI no dey guess. If e no know, e go tell you make you see doctor." },
      { q: "How I fit use the voice feature?", a: "Press the mic button, talk wetin dey do you, then press stop. E go write wetin you talk and answer you. You fit press Listen make e read am for you." },
      { q: "Wetin make I do for medical emergency?", a: "If person no fit breathe well, get chest pain, dey bleed, or faint, no use HealthBridge. Go nearest hospital straight or call emergency number." }
    ]
  },
  Swahili: { 
    title: "Msaada na Maswali", 
    desc: "Maswali ya kawaida kuhusu HealthBridge Africa", 
    footer: "⚕️ HealthBridge Africa sio huduma ya matibabu. Daima shauriana na daktari.",
    faqs: [
      { q: "Je, HealthBridge Africa inaweza kuchukua nafasi ya daktari?", a: "Hapana, hii ni zana ya habari za afya, sio huduma ya matibabu. Daima shauriana na daktari kwa matibabu." },
      { q: "Ni lugha gani zinazotumika?", a: "Kiingereza, Pidgin, Kiswahili, Oromo, Twi, na Kiamhari. Unaweza kubadilisha wakati wowote." },
      { q: "Je, mazungumzo yangu ni ya faragha?", a: "Ndio, mazungumzo yako yanahifadhiwa kwa usalama na kifaa chako pekee. Hatukusanyi jina lako." },
      { q: "Taarifa hizi ni sahihi kiasi gani?", a: "Majibu yanatoka kwa vyanzo vilivyothibitishwa kama WHO. AI haibashiri. Kama haina uhakika, itakushauri umuone daktari." },
      { q: "Ninatumiaje kipengele cha sauti?", a: "Gusa kitufe cha kipaza sauti, ongea, kisha gusa simamisha. Unaweza kusikiliza majibu pia." },
      { q: "Nifanye nini wakati wa dharura?", a: "Kama ni dharura ya kiafya (kama kushindwa kupumua), nenda hospitali mara moja." }
    ]
  },
  Twi: { 
    title: "Mmoa & Nsɛmbisa", 
    desc: "Nsɛm a nkurɔfoɔ taa bisa fa HealthBridge ho", 
    footer: "⚕️ HealthBridge Africa nyɛ ayaresabea. Bere biara kɔhunu oduruyɛfoɔ a ɔwɔ tumi krataa.",
    faqs: [
      { q: "HealthBridge Africa bɛtumi asi oduruyɛfoɔ ananmu?", a: "Dabi, ɛyɛ afutuo nko ara, ɛnyɛ ayaresabea. Kɔhunu oduruyɛfoɔ bere biara." },
      { q: "Kasa bɛn na yɛde di dwuma?", a: "English, Pidgin, Swahili, Oromo, Twi, ne Amharic. Wobɛtumi asesa no bere biara." },
      { q: "Me nsɛm yɛ kokoam?", a: "Aane, wo nsɛm no yɛ kokoam, yɛnkora wo din anaa email so." },
      { q: "Nsɛm no yɛ nokware?", a: "Nsɛm no firi mmeaeɛ a wɔagye atom te sɛ WHO. AI no ntwen nkyerɛ." },
      { q: "Mɛyɛ sɛn ade nne afiri no awura mu?", a: "Mia mic no so, kasa, na mia stop. Wobɛtumi atie mmuaeɛ no bio." },
      { q: "Sɛ asiane ba a mɛyɛ dɛn?", a: "Sɛ obi ntumi ngye ahome anaa ɔrepira a, kɔ ayaresabea a ɛbɛn wo ntɛm ara." }
    ]
  },
  Oromo: { 
    title: "Gargaarsa & Gaaffii", 
    desc: "Gaaffiilee yeroo baay'ee HealthBridge Africa irratti gaafataman", 
    footer: "⚕️ HealthBridge Africa tajaajila yaalaa miti. Yeroo mara ogeessa fayyaa mariisisi.",
    faqs: [
      { q: "HealthBridge Africa ogeessa fayyaa bakka ni bu'aa?", a: "Lakki, kun meeshaa odeeffannoo fayyaa ti, tajaajila yaalaa miti. Yeroo mara ogeessa fayyaa mariisisi." },
      { q: "Afaanota kamtu jira?", a: "Ingiliffa, Piijiinii, Suwaahilii, Oromoo, Twi, fi Amaariffa. Yeroo barbaaddetti jijjiiruu dandeessa." },
      { q: "Mariin koo iccitiidhaa?", a: "Eeyyee, mariin kee iccitiidhaan eegama, maqaa kees hin sassaabnu." },
      { q: "Odeeffannoon kun sirriidhaa?", a: "Deebiin kun madda mirkanaa'e akka WHO irraa dhufa. AI'n tilmaama hin kennu." },
      { q: "Sagalee akkamittan fayyadama?", a: "Mallattoo maayikii tuqi, dubbadhu, itti aanee dhaabi. Deebii isaas dhaggeeffachuu dandeessa." },
      { q: "Balaa tasaa yoo mudate maal gochuun qaba?", a: "Yoo rakkoon harganuu, dhukkubbii qomaa ykn dhiigni baay'een jiraate, dafii gara mana yaalaa deemi." }
    ]
  },
  Amharic: { 
    title: "እገዛ እና ጥያቄዎች", 
    desc: "ስለ HealthBridge Africa የተለመዱ ጥያቄዎች", 
    footer: "⚕️ HealthBridge Africa የህክምና አገልግሎት አይደለም። ሁልጊዜ ዶክተር ያማክሩ።",
    faqs: [
      { q: "HealthBridge Africa የዶክተር ምትክ ነው?", a: "አላለም፣ ይህ የጤና መረጃ መሳሪያ እንጂ የህክምና አገልግሎት አይደለም። ሁልጊዜ ዶክተር ያማክሩ።" },
      { q: "ምን ቋንቋዎች ይደገፋሉ?", a: "እንግሊዝኛ፣ ፒጂን፣ ስዋሂሊ፣ ኦሮሞ፣ ትዊ እና አማርኛ። በማንኛውም ጊዜ መቀየር ይችላሉ።" },
      { q: "ውይይቴ ሚስጥራዊ ነው?", a: "አዎ፣ ውይይቶችዎ ደህንነታቸው የተጠበቀ ነው። ስምዎን አንሰበስብም።" },
      { q: "መረጃው ምን ያህል ትክክል ነው?", a: "ምላሾቹ እንደ WHO ካሉ የተረጋገጡ ምንጮች የተገኙ ናቸው። AI አይገምትም።" },
      { q: "የድምጽ ባህሪውን እንዴት እጠቀማለሁ?", a: "ማይክሮፎኑን ይጫኑ፣ ይናገሩ፣ ከዚያ ያቁሙ። ምላሹን ማዳመጥም ይችላሉ።" },
      { q: "በድንገተኛ አደጋ ጊዜ ምን ላድርግ?", a: "የመተንፈስ ችግር ወይም ከባድ የደም መፍሰስ ካለ፣ ወዲያውኑ ወደ ሆስፒታል ይሂዱ።" }
    ]
  }
};

function FAQItem({ question, answer }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    // FIX: Added 'shrink-0' so the flex container doesn't crush the items when they open!
    <div className="border border-health-border rounded-xl overflow-hidden shrink-0">
      <button onClick={() => setIsOpen(!isOpen)} className="w-full flex items-center justify-between p-4 text-left bg-health-surface hover:bg-health-chat transition-colors">
        <span className="text-sm font-bold text-health-textPrimary pr-4 leading-snug">{question}</span>
        <span className="flex-shrink-0">
          {isOpen ? <ChevronUp size={16} className="text-health-accentLight" /> : <ChevronDown size={16} className="text-health-textSecondary" />}
        </span>
      </button>
      {isOpen && (
        <div className="px-4 pb-4 bg-health-chat border-t border-health-border/50">
          <p className="text-sm text-health-textSecondary leading-relaxed pt-3">{answer}</p>
        </div>
      )}
    </div>
  );
}

export default function HelpModal({ onClose, language }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS['English'];

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-health-surface rounded-2xl shadow-2xl w-full max-w-lg border border-health-border flex flex-col max-h-[85vh]">

        <div className="flex items-center justify-between p-5 border-b border-health-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-health-chat border border-health-border flex items-center justify-center flex-shrink-0">
              <HelpCircle size={18} className="text-health-accent" />
            </div>
            <div>
              <h2 className="text-lg font-brand font-bold text-health-textPrimary leading-tight">{t.title}</h2>
              <p className="text-xs text-health-textSecondary">{t.desc}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-health-chat rounded-lg text-health-textSecondary hover:text-health-textPrimary transition-colors flex-shrink-0 ml-2">
            <X size={18} />
          </button>
        </div>

        <div className="overflow-y-auto p-5 flex flex-col gap-3 hide-scrollbar">
          {t.faqs.map((faq, index) => (
            <FAQItem key={index} question={faq.q} answer={faq.a} />
          ))}
        </div>

        <div className="p-4 border-t border-health-border flex-shrink-0">
          <p className="text-[11px] text-health-textSecondary/70 text-center">{t.footer}</p>
        </div>
      </div>
    </div>
  );
}