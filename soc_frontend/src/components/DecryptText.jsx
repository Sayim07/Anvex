// DecryptText.jsx — Cyberpunk / Matrix alphanumeric text decryption scramble effect
import { useState, useEffect } from 'react';

const CYBER_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*<>[]{}';

export default function DecryptText({ text, speed = 25, enabled = true, className = '' }) {
  const [displayText, setDisplayText] = useState(text);

  useEffect(() => {
    if (!enabled || !text) {
      setDisplayText(text);
      return;
    }

    let iteration = 0;
    const targetLength = text.length;

    const interval = setInterval(() => {
      setDisplayText(() => {
        return text
          .split('')
          .map((char, index) => {
            if (index < iteration) {
              return text[index];
            }
            if (char === ' ') return ' ';
            return CYBER_CHARS[Math.floor(Math.random() * CYBER_CHARS.length)];
          })
          .join('');
      });

      if (iteration >= targetLength) {
        clearInterval(interval);
      }

      iteration += 1;
    }, speed);

    return () => clearInterval(interval);
  }, [text, enabled, speed]);

  return <span className={className}>{displayText}</span>;
}
