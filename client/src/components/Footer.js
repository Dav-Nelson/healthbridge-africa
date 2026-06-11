import React from 'react';

export default function Footer({ language }) {
  // Dictionary for footer translations
  const footerTranslations = {
    English: "This is not a substitute for professional medical advice. Always consult a doctor.",
    Pidgin: "Dis one no mean say make you no go hospital. Make you always see doctor.",
    Swahili: "Hii sio mbadala wa ushauri wa kitaalamu wa matibabu. Daima wasiliana na daktari.",
    Oromo: "Kun gorsa ogeessa fayyaa bakka hin bu'u. Yeroo hundumaa hakiimii mariyachiisaa.",
    Twi: "Eyi nnyɛ aduruyɛ mu afotu a efi abenfo hɔ ananmu. Kɔ hu dɔkota bere nyinaa."
  };

  const text = footerTranslations[language] || footerTranslations.English;

  return (
    <footer className="bg-slate-800 text-slate-400 py-4 text-center text-xs md:text-sm">
      <p>{text}</p>
    </footer>
  );
}