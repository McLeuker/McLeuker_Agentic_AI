"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { Sector } from "@/contexts/SectorContext";
import Image from "next/image";

// ─── Image data per domain ───────────────────────────────────────────
interface MoodImage {
  src: string;
  alt: string;
  span: "tall" | "wide" | "normal"; // masonry sizing
}

const DOMAIN_IMAGES: Record<string, MoodImage[]> = {
  fashion: [
    { src: "/moodboard/fashion_1.jpg", alt: "Haute couture silhouette", span: "tall" },
    { src: "/moodboard/fashion_2.jpg", alt: "Draped fabric detail", span: "normal" },
    { src: "/moodboard/fashion_3.jpg", alt: "Fashion editorial close-up", span: "wide" },
    { src: "/moodboard/fashion_4.jpg", alt: "Tailoring craftsmanship", span: "normal" },
    { src: "/moodboard/fashion_5.jpg", alt: "Minimalist fashion portrait", span: "tall" },
    { src: "/moodboard/fashion_6.jpg", alt: "Model in motion", span: "normal" },
    { src: "/moodboard/fashion_7.jpg", alt: "Accessories still life", span: "wide" },
    { src: "/moodboard/fashion_8.jpg", alt: "Fashion atelier workspace", span: "normal" },
  ],
  beauty: [
    { src: "/moodboard/beauty_1.jpg", alt: "Beauty portrait close-up", span: "tall" },
    { src: "/moodboard/beauty_2.jpg", alt: "Skincare texture detail", span: "normal" },
    { src: "/moodboard/beauty_3.jpg", alt: "Professional makeup tools", span: "wide" },
    { src: "/moodboard/beauty_4.jpg", alt: "Natural beauty ingredients", span: "normal" },
    { src: "/moodboard/beauty_5.jpg", alt: "Beauty ritual moment", span: "normal" },
    { src: "/moodboard/beauty_6.jpg", alt: "Cosmetics arrangement", span: "tall" },
    { src: "/moodboard/beauty_7.jpg", alt: "Beauty editorial lighting", span: "wide" },
    { src: "/moodboard/beauty_8.jpg", alt: "Elegant hands detail", span: "normal" },
  ],
  skincare: [
    { src: "/moodboard/skincare_1.jpg", alt: "Skincare formulation", span: "normal" },
    { src: "/moodboard/skincare_2.jpg", alt: "Natural ingredients close-up", span: "tall" },
    { src: "/moodboard/skincare_3.jpg", alt: "Laboratory research", span: "wide" },
    { src: "/moodboard/skincare_4.jpg", alt: "Botanical extracts", span: "normal" },
    { src: "/moodboard/skincare_5.jpg", alt: "Skincare ritual", span: "tall" },
    { src: "/moodboard/skincare_6.jpg", alt: "Clean beauty products", span: "normal" },
    { src: "/moodboard/skincare_7.jpg", alt: "Skin texture macro", span: "wide" },
    { src: "/moodboard/skincare_8.jpg", alt: "Wellness ingredients", span: "normal" },
  ],
  sustainability: [
    { src: "/moodboard/sustainability_1.jpg", alt: "Organic cotton field", span: "wide" },
    { src: "/moodboard/sustainability_2.jpg", alt: "Recycled materials", span: "normal" },
    { src: "/moodboard/sustainability_3.jpg", alt: "Recycled fabric scraps", span: "tall" },
    { src: "/moodboard/sustainability_4.jpg", alt: "Eco-friendly production", span: "normal" },
    { src: "/moodboard/sustainability_5.jpg", alt: "Natural dyeing process", span: "normal" },
    { src: "/moodboard/sustainability_6.jpg", alt: "Sustainable packaging", span: "wide" },
    { src: "/moodboard/sustainability_7.jpg", alt: "Upcycled fashion", span: "tall" },
    { src: "/moodboard/sustainability_8.jpg", alt: "Cotton plant detail", span: "normal" },
  ],
  "fashion-tech": [
    { src: "/moodboard/fashion_tech_1.jpg", alt: "Wearable technology", span: "wide" },
    { src: "/moodboard/fashion_tech_2.jpg", alt: "3D printed fashion", span: "tall" },
    { src: "/moodboard/fashion_tech_3.jpg", alt: "Digital fashion design", span: "normal" },
    { src: "/moodboard/fashion_tech_4.jpg", alt: "Robotic manufacturing", span: "wide" },
    { src: "/moodboard/fashion_tech_5.jpg", alt: "AR fashion experience", span: "tall" },
    { src: "/moodboard/fashion_tech_6.jpg", alt: "Smart fabric innovation", span: "normal" },
    { src: "/moodboard/fashion_tech_7.jpg", alt: "Laser cutting precision", span: "normal" },
    { src: "/moodboard/fashion_tech_8.jpg", alt: "Body scanning technology", span: "tall" },
  ],
  catwalks: [
    { src: "/moodboard/catwalks_1.jpg", alt: "Model on the runway", span: "tall" },
    { src: "/moodboard/catwalks_2.jpg", alt: "Backstage preparation", span: "wide" },
    { src: "/moodboard/catwalks_3.jpg", alt: "Runway detail close-up", span: "normal" },
    { src: "/moodboard/catwalks_4.jpg", alt: "Empty runway spotlights", span: "wide" },
    { src: "/moodboard/catwalks_5.jpg", alt: "Front row audience", span: "tall" },
    { src: "/moodboard/catwalks_6.jpg", alt: "Finale walk", span: "normal" },
    { src: "/moodboard/catwalks_7.jpg", alt: "Avant-garde beauty look", span: "normal" },
    { src: "/moodboard/catwalks_8.jpg", alt: "Designer bow moment", span: "tall" },
  ],
  culture: [
    { src: "/moodboard/culture_1.jpg", alt: "Contemporary art gallery", span: "wide" },
    { src: "/moodboard/culture_2.jpg", alt: "Street art mural", span: "tall" },
    { src: "/moodboard/culture_3.jpg", alt: "Analog photography tools", span: "normal" },
    { src: "/moodboard/culture_4.jpg", alt: "Ballet dancer in motion", span: "wide" },
    { src: "/moodboard/culture_5.jpg", alt: "Pottery craftsmanship", span: "tall" },
    { src: "/moodboard/culture_6.jpg", alt: "Modern museum architecture", span: "normal" },
    { src: "/moodboard/culture_7.jpg", alt: "Live music atmosphere", span: "wide" },
    { src: "/moodboard/culture_8.jpg", alt: "Literary bookshop interior", span: "tall" },
  ],
  textile: [
    { src: "/moodboard/textile_1.jpg", alt: "Woven fabric macro", span: "normal" },
    { src: "/moodboard/textile_2.jpg", alt: "Fabric rolls warehouse", span: "wide" },
    { src: "/moodboard/textile_3.jpg", alt: "Traditional loom weaving", span: "tall" },
    { src: "/moodboard/textile_4.jpg", alt: "Draped silk detail", span: "wide" },
    { src: "/moodboard/textile_5.jpg", alt: "Cotton bolls natural fiber", span: "normal" },
    { src: "/moodboard/textile_6.jpg", alt: "Thread spools arrangement", span: "tall" },
    { src: "/moodboard/textile_7.jpg", alt: "Pattern cutting atelier", span: "wide" },
    { src: "/moodboard/textile_8.jpg", alt: "Cable knit texture", span: "normal" },
  ],
  lifestyle: [
    { src: "/moodboard/lifestyle_1.jpg", alt: "Minimalist interior", span: "wide" },
    { src: "/moodboard/lifestyle_2.jpg", alt: "Yoga practice", span: "tall" },
    { src: "/moodboard/lifestyle_3.jpg", alt: "Artisan coffee culture", span: "normal" },
    { src: "/moodboard/lifestyle_4.jpg", alt: "Curated living space", span: "wide" },
    { src: "/moodboard/lifestyle_5.jpg", alt: "Farmers market stroll", span: "tall" },
    { src: "/moodboard/lifestyle_6.jpg", alt: "Elegant table setting", span: "normal" },
    { src: "/moodboard/lifestyle_7.jpg", alt: "Urban cycling lifestyle", span: "normal" },
    { src: "/moodboard/lifestyle_8.jpg", alt: "Flower arrangement", span: "tall" },
  ],
};

// ─── Lightbox component ──────────────────────────────────────────────
function Lightbox({
  image,
  onClose,
}: {
  image: MoodImage;
  onClose: () => void;
}) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm cursor-pointer"
      onClick={onClose}
    >
      <div
        className="relative max-w-[90vw] max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <img
          src={image.src}
          alt={image.alt}
          className="max-w-full max-h-[90vh] object-contain rounded-lg"
        />
        <button
          onClick={onClose}
          className="absolute -top-3 -right-3 w-8 h-8 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white/70 hover:text-white transition-all"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
        <p className="text-center text-white/50 text-xs mt-3 tracking-wide">
          {image.alt}
        </p>
      </div>
    </div>
  );
}

// ─── Main MoodBoard component ────────────────────────────────────────
interface MoodBoardProps {
  sector: Sector;
}

export function MoodBoard({ sector }: MoodBoardProps) {
  const [selectedImage, setSelectedImage] = useState<MoodImage | null>(null);
  const [loadedImages, setLoadedImages] = useState<Set<number>>(new Set());

  const images = useMemo(() => {
    return DOMAIN_IMAGES[sector] || DOMAIN_IMAGES["fashion"];
  }, [sector]);

  const handleImageLoad = useCallback((index: number) => {
    setLoadedImages((prev) => new Set(prev).add(index));
  }, []);

  // Don't render for "global" sector
  if (sector === ("global" as Sector)) return null;

  return (
    <section className="relative py-16 md:py-24 overflow-hidden">
      {/* Subtle background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#070707] via-[#0a0a0a] to-[#070707]" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="mb-10 md:mb-14">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-px w-8 bg-white/20" />
            <span className="text-[11px] uppercase tracking-[0.2em] text-white/40 font-medium">
              Visual Intelligence
            </span>
          </div>
          <h2 className="font-serif text-3xl md:text-4xl text-white/[0.95] tracking-tight">
            Curated Mood Board
          </h2>
          <p className="text-[15px] text-white/50 max-w-md leading-relaxed mt-1">
            Curated visual inspiration that captures the look, feel, and momentum
          </p>
        </div>

        {/* Pinterest-style masonry grid */}
        <div className="columns-2 md:columns-3 lg:columns-4 gap-3 md:gap-4 space-y-3 md:space-y-4">
          {images.map((image, index) => (
            <div
              key={`${sector}-${index}`}
              className={`
                break-inside-avoid group cursor-pointer relative overflow-hidden rounded-lg
                ${image.span === "tall" ? "aspect-[3/4]" : ""}
                ${image.span === "wide" ? "aspect-[4/3]" : ""}
                ${image.span === "normal" ? "aspect-square" : ""}
              `}
              onClick={() => setSelectedImage(image)}
            >
              {/* Loading skeleton */}
              {!loadedImages.has(index) && (
                <div className="absolute inset-0 bg-white/[0.03] animate-pulse rounded-lg" />
              )}

              {/* Image */}
              <img
                src={image.src}
                alt={image.alt}
                loading={index < 4 ? "eager" : "lazy"}
                onLoad={() => handleImageLoad(index)}
                className={`
                  w-full h-full object-cover transition-all duration-700 ease-out
                  ${loadedImages.has(index) ? "opacity-100" : "opacity-0"}
                  group-hover:scale-[1.03] group-hover:brightness-110
                  grayscale
                `}
              />

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              {/* Caption on hover */}
              <div className="absolute bottom-0 left-0 right-0 p-3 translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-out">
                <p className="text-[11px] text-white/70 font-light tracking-wide">
                  {image.alt}
                </p>
              </div>

              {/* Corner accent */}
              <div className="absolute top-2 right-2 w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <svg viewBox="0 0 20 20" fill="none" className="w-full h-full">
                  <circle cx="10" cy="10" r="9" stroke="white" strokeOpacity="0.3" strokeWidth="1" />
                  <path d="M7 10H13M10 7V13" stroke="white" strokeOpacity="0.5" strokeWidth="1" strokeLinecap="round" />
                </svg>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Lightbox */}
      {selectedImage && (
        <Lightbox image={selectedImage} onClose={() => setSelectedImage(null)} />
      )}
    </section>
  );
}
