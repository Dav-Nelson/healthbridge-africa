import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Copy, Check, Share2, ShieldCheck, ImageOff } from 'lucide-react';
import ResponsePlayer from './ResponsePlayer';

// (Keep your DISEASE_IMAGE_MAP exactly as it was)
const DISEASE_IMAGE_MAP = {
  malaria: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Malaria_Parasite_Connecting_to_Human_Red_Blood_Cell_%2813705855823%29.jpg/320px-Malaria_Parasite_Connecting_to_Human_Red_Blood_Cell_%2813705855823%29.jpg', alt: 'Malaria parasite connecting to a red blood cell', label: 'Malaria — parasite infecting red blood cells', credit: 'NIH / Wikimedia Commons' },
  typhoid: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Rose_spots_typhoid_fever.jpg/320px-Rose_spots_typhoid_fever.jpg', alt: 'Rose spots on skin', label: 'Typhoid — characteristic rose spots on the trunk', credit: 'Wikimedia Commons' },
  cholera: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Cholera_hospital_in_Dhaka.jpg/320px-Cholera_hospital_in_Dhaka.jpg', alt: 'Cholera patient', label: 'Cholera — severe dehydration requiring immediate ORS', credit: 'Wikimedia Commons' },
  measles: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Morbillivirus_measles_infection.jpg/320px-Morbillivirus_measles_infection.jpg', alt: 'Measles rash', label: 'Measles — blotchy rash spreading from face downward', credit: 'CDC / Wikimedia Commons' },
  chickenpox: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Varicella_%28chickenpox%29_in_a_17-year-old_male.jpg/240px-Varicella_%28chickenpox%29_in_a_17-year-old_male.jpg', alt: 'Chickenpox blisters', label: 'Chickenpox — fluid-filled blisters', credit: 'Wikimedia Commons' },
  mpox: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/856/Monkeypox_virus_skin_lesions_%282022%29.jpg/320px-Monkeypox_virus_skin_lesions_%282022%29.jpg', alt: 'Mpox skin lesions', label: 'Mpox — deep-seated lesions on darker skin', credit: 'CDC / Wikimedia Commons' },
  monkeypox: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/856/Monkeypox_virus_skin_lesions_%282022%29.jpg/320px-Monkeypox_virus_skin_lesions_%282022%29.jpg', alt: 'Mpox skin lesions', label: 'Mpox — deep-seated lesions on darker skin', credit: 'CDC / Wikimedia Commons' },
  meningitis: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Meningitis_petechial_rash.jpg/320px-Meningitis_petechial_rash.jpg', alt: 'Non-blanching petechial rash', label: 'Meningitis — non-blanching petechial rash (medical emergency)', credit: 'Wikimedia Commons' },
  dengue: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Denguerash.JPG/320px-Denguerash.JPG', alt: 'Dengue fever rash', label: 'Dengue — characteristic rash appearing 3–4 days into fever', credit: 'Wikimedia Commons' },
  scabies: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Scabies_2.jpg/320px-Scabies_2.jpg', alt: 'Scabies burrow tracks', label: 'Scabies — burrow tracks and rash between fingers', credit: 'Wikimedia Commons' },
  ringworm: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Ringworm_on_the_arm_or_Tinea_corporis_on_the_arm.jpg/320px-Ringworm_on_the_arm_or_Tinea_corporis_on_the_arm.jpg', alt: 'Ringworm lesion', label: 'Ringworm (Tinea) — circular ring-shaped lesion', credit: 'Wikimedia Commons' },
  eczema: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Atopic_dermatitis_child_2.jpg/240px-Atopic_dermatitis_child_2.jpg', alt: 'Eczema on child', label: 'Eczema — dry, inflamed skin patches', credit: 'Wikimedia Commons' },
  conjunctivitis: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/An_eye_with_viral_conjunctivitis.jpg/320px-An_eye_with_viral_conjunctivitis.jpg', alt: 'Red eye', label: 'Conjunctivitis (Apollo) — red, inflamed eye with discharge', credit: 'Wikimedia Commons' },
  apollo: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/An_eye_with_viral_conjunctivitis.jpg/320px-An_eye_with_viral_conjunctivitis.jpg', alt: 'Red eye', label: 'Conjunctivitis (Apollo) — red, inflamed eye with discharge', credit: 'Wikimedia Commons' },
  jaundice: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Jaundice_eye.jpg/320px-Jaundice_eye.jpg', alt: 'Jaundice eye', label: 'Jaundice — yellowing of the whites of the eyes', credit: 'Wikimedia Commons' },
  malnutrition: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Starved_child.jpg/240px-Starved_child.jpg', alt: 'Malnourished child', label: 'Severe Acute Malnutrition — visible wasting in a child', credit: 'Wikimedia Commons' },
  tuberculosis: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/TB_poster.jpg/240px-TB_poster.jpg', alt: 'TB chest X-ray', label: 'Tuberculosis (TB) — airborne disease affecting the lungs', credit: 'Wikimedia Commons' },
  tb: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/TB_poster.jpg/240px-TB_poster.jpg', alt: 'TB chest X-ray', label: 'Tuberculosis (TB) — airborne disease affecting the lungs', credit: 'Wikimedia Commons' },
  'sickle cell': { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Sickle_cell_01.jpg/320px-Sickle_cell_01.jpg', alt: 'Sickle cells', label: 'Sickle Cell Disease — abnormal sickle-shaped red blood cells', credit: 'Wikimedia Commons' },
  schistosomiasis: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Schistosomiasis_bladder_histopathology.jpg/320px-Schistosomiasis_bladder_histopathology.jpg', alt: 'Schistosomiasis tissue', label: 'Schistosomiasis (Bilharzia) — parasitic disease from freshwater contact', credit: 'Wikimedia Commons' },
  bilharzia: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Schistosomiasis_bladder_histopathology.jpg/320px-Schistosomiasis_bladder_histopathology.jpg', alt: 'Schistosomiasis tissue', label: 'Schistosomiasis (Bilharzia) — parasitic disease from freshwater contact', credit: 'Wikimedia Commons' },
  'lassa fever': { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Lassa_fever_virus.jpg/320px-Lassa_fever_virus.jpg', alt: 'Lassa fever virus', label: 'Lassa Fever — hemorrhagic viral fever endemic to West Africa', credit: 'CDC / Wikimedia Commons' },
  hypertension: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Blutdruckmessun_Sphygmomanometer.jpg/320px-Blutdruckmessun_Sphygmomanometer.jpg', alt: 'Blood pressure measurement', label: 'Hypertension — the silent killer; regular monitoring is essential', credit: 'Wikimedia Commons' },
  diabetes: { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Diabetes_patient_taking_blood_sugar.jpg/320px-Diabetes_patient_taking_blood_sugar.jpg', alt: 'Blood sugar check', label: 'Diabetes — regular blood glucose monitoring is essential', credit: 'Wikimedia Commons' },
};

function detectCondition(text) {
  if (!text) return null;
  const lower = text.toLowerCase();
  const orderedKeys = ['lassa fever', 'sickle cell', 'mpox', 'monkeypox', 'chickenpox', 'conjunctivitis', 'apollo', 'ringworm', 'schistosomiasis', 'bilharzia', 'meningitis', 'malnutrition', 'tuberculosis', 'dengue', 'jaundice', 'scabies', 'eczema', 'cholera', 'typhoid', 'measles', 'malaria', 'hypertension', 'diabetes', 'tb'];
  for (const key of orderedKeys) {
    if (lower.includes(key)) return key;
  }
  return null;
}

function DiseaseImage({ conditionKey }) {
  const [imgError, setImgError] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);
  const data = DISEASE_IMAGE_MAP[conditionKey];
  if (!data) return null;

  return (
    <div className="mt-3 rounded-xl overflow-hidden border border-health-border bg-health-surface">
      {!imgError ? (
        <>
          <div className={`w-full bg-health-chat flex items-center justify-center ${imgLoaded ? 'hidden' : 'h-32'}`}>
            <div className="w-6 h-6 border-2 border-health-accent border-t-transparent rounded-full animate-spin" />
          </div>
          <img
            src={data.url}
            alt={data.alt}
            onLoad={() => setImgLoaded(true)}
            onError={() => setImgError(true)}
            className={`w-full max-h-52 object-cover ${imgLoaded ? 'block' : 'hidden'}`}
          />
        </>
      ) : (
        <div className="h-20 flex items-center justify-center gap-2 text-health-textSecondary text-xs">
          <ImageOff size={16} />
          <span>Image unavailable</span>
        </div>
      )}
      <div className="px-3 py-2 border-t border-health-border bg-health-chat/50">
        <p className="text-xs font-medium text-health-textPrimary">{data.label}</p>
        <p className="text-[10px] text-health-textSecondary opacity-70 mt-0.5">Source: {data.credit} · For clinical reference only</p>
      </div>
    </div>
  );
}

export default function BotMessageBubble({ text, language }) {
  const [feedback, setFeedback] = useState(null);
  const [isCopied, setIsCopied] = useState(false);
  const detectedCondition = detectCondition(text);

  const handleFeedback = (type) => setFeedback(type);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {}
  };
  const handleShare = async () => {
    if (navigator.share) {
      try { await navigator.share({ title: 'HealthBridge Africa', text }); } catch (err) {}
    } else {
      await handleCopy();
      alert('Response copied to clipboard to share!');
    }
  };

  return (
    <div className="max-w-[92%] md:max-w-[85%] rounded-[18px] rounded-tl-[4px] px-4 py-3 md:px-5 md:py-4 bg-health-aiBubble text-health-textPrimary self-start shadow-sm">
      
      <div className="flex items-center gap-1.5 mb-2 text-health-accentLight">
        <ShieldCheck size={14} />
        <span className="text-[10px] font-bold uppercase tracking-widest font-brand">HealthBridge</span>
      </div>

      <p className="leading-relaxed text-[15px] whitespace-pre-line">{text}</p>

      {detectedCondition && <DiseaseImage conditionKey={detectedCondition} />}

      <div className="mt-3 flex flex-wrap items-center justify-between border-t border-health-border/50 pt-3 gap-2">
        <ResponsePlayer text={text} language={language} />

        <div className="flex items-center gap-1">
          <button onClick={handleCopy} title="Copy response" className="p-1.5 text-health-textSecondary hover:text-health-accent hover:bg-health-surface rounded-md transition-colors">
            {isCopied ? <Check size={16} className="text-health-accent" /> : <Copy size={16} />}
          </button>

          <button onClick={handleShare} title="Share response" className="p-1.5 text-health-textSecondary hover:text-health-accent hover:bg-health-surface rounded-md transition-colors">
            <Share2 size={16} />
          </button>

          <div className="w-px h-4 bg-health-border mx-1" />

          <button onClick={() => handleFeedback('up')} className={`p-1.5 rounded-md transition-colors ${feedback === 'up' ? 'text-health-bg bg-health-accent' : 'text-health-textSecondary hover:text-health-accent hover:bg-health-surface'}`}>
            <ThumbsUp size={16} className={feedback === 'up' ? 'fill-current' : ''} />
          </button>

          <button onClick={() => handleFeedback('down')} className={`p-1.5 rounded-md transition-colors ${feedback === 'down' ? 'text-health-bg bg-red-600' : 'text-health-textSecondary hover:text-red-500 hover:bg-health-surface'}`}>
            <ThumbsDown size={16} className={feedback === 'down' ? 'fill-current' : ''} />
          </button>
        </div>
      </div>
    </div>
  );
}