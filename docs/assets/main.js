document.documentElement.classList.add("js");

const navItems = document.querySelectorAll("[data-category]");

const setActive = (target) => {
  navItems.forEach((item) => {
    item.classList.toggle("is-active", item.dataset.category === target);
  });
};

const clearActive = () => {
  navItems.forEach((item) => item.classList.remove("is-active"));
};

navItems.forEach((item) => {
  item.addEventListener("mouseenter", () => setActive(item.dataset.category));
  item.addEventListener("focus", () => setActive(item.dataset.category));
  item.addEventListener("blur", clearActive);
});

document.querySelector(".category-nav")?.addEventListener("mouseleave", clearActive);

const getTitleFromImagePath = (path) => {
  const fileName = decodeURIComponent(path.split("/").pop() || "");
  const withoutExtension = fileName.replace(/\.[^.]+$/, "");
  const spaced = withoutExtension
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  return spaced;
};

document.querySelectorAll(".work-entry").forEach((entry) => {
  const image = entry.querySelector(".piece-image img");
  const title = entry.querySelector("[data-title-from='image'] .title-text");

  if (!image || !title) return;

  const generatedTitle = getTitleFromImagePath(image.getAttribute("src") || "");
  if (generatedTitle) {
    title.textContent = generatedTitle;
  }
});

const observeSoftReveal = (targets, options) => {
  if (!targets.length) return;

  if (!("IntersectionObserver" in window)) {
    targets.forEach((target) => target.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("is-visible", entry.isIntersecting);
    });
  }, options);

  targets.forEach((target, index) => {
    if (index === 0) {
      target.classList.add("is-visible");
    }
    observer.observe(target);
  });
};

observeSoftReveal(Array.from(document.querySelectorAll(".work-entry")), {
  root: null,
  rootMargin: "-14% 0px -14% 0px",
  threshold: 0.35,
});

document.querySelectorAll("[data-slider-track]").forEach((track) => {
  observeSoftReveal(Array.from(track.querySelectorAll(".detail-slide")), {
    root: track,
    rootMargin: "-10% 0px -10% 0px",
    threshold: 0.42,
  });
});

if (window.location.protocol.startsWith("http")) {
  let currentSiteVersion = null;

  const checkForSiteUpdates = async () => {
    try {
      const response = await fetch(`/site-version.json?time=${Date.now()}`, {
        cache: "no-store",
      });
      if (!response.ok) return;

      const data = await response.json();
      if (!data.version) return;

      if (currentSiteVersion === null) {
        currentSiteVersion = data.version;
        return;
      }

      if (data.version !== currentSiteVersion) {
        window.location.reload();
      }
    } catch {
      // The static fallback can be opened without the Python server.
    }
  };

  checkForSiteUpdates();
  window.setInterval(checkForSiteUpdates, 1500);
}

