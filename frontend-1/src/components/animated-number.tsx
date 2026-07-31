import { useEffect, useRef, useState } from "react";

export function AnimatedNumber({
  value,
  duration = 900,
  suffix = "",
  decimals = 0,
}: { value: number; duration?: number; suffix?: string; decimals?: number }) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef<number | null>(null);
  const fromRef = useRef(0);

  useEffect(() => {
    const shouldAnimate = localStorage.getItem('animatedCounters') !== 'false';
    if (!shouldAnimate) {
      setDisplay(value);
      return;
    }

    fromRef.current = display;
    startRef.current = null;
    let raf = 0;
    const step = (t: number) => {
      if (startRef.current === null) startRef.current = t;
      const p = Math.min(1, (t - startRef.current) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(fromRef.current + (value - fromRef.current) * eased);
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, duration]);

  return <span>{display.toFixed(decimals)}{suffix}</span>;
}
