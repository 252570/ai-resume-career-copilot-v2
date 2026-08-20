"use client";

/* Quiet Signal Studio: the generated compass-document logo remains primary; this CSS fallback preserves the same silhouette if the managed asset is still resolving. */
import { useState } from "react";

export function BrandMark() {
  const [assetUnavailable, setAssetUnavailable] = useState(false);

  return (
    <span className="mark" aria-hidden="true">
      {!assetUnavailable && (
        <img
          src="/manus-storage/copilot-mark_3c7f9347.png"
          alt=""
          onError={() => setAssetUnavailable(true)}
        />
      )}
      {assetUnavailable && <span className="mark-fallback" />}
    </span>
  );
}
