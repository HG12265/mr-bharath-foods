import Image from "next/image";
import type { ReactNode } from "react";

/** Shared presentation only: existing page copy, links and actions are supplied unchanged. */
export default function PageBanner({
  children,
  image,
  alt,
  variant = "inner",
  imageClassName = "",
}: {
  children: ReactNode;
  image: string;
  alt: string;
  variant?: "home" | "inner" | "about";
  imageClassName?: string;
}) {
  return (
    <section className={`reference-banner reference-banner--${variant}`}>
      <div className="reference-banner__media">
        {variant === "home" ? (
          <svg className="reference-banner__image" viewBox="303 82 532 402" preserveAspectRatio="xMidYMid slice" role="img" aria-label={alt}>
            <image href="/images/extracted_image1.png" width="835" height="1883" />
          </svg>
        ) : (
        <Image
          src={image}
          alt={alt}
          fill
          priority
          sizes="(max-width: 767px) 100vw, 62vw"
          quality={95}
          className={`reference-banner__image ${imageClassName}`}
        />
        )}
      </div>
      <div className="reference-banner__container">
        <div className="reference-banner__content">{children}</div>
      </div>
    </section>
  );
}
