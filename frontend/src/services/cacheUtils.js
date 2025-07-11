// cacheUtils.js

const CACHE_PREFIX = {
    SPECIES_MATCH: 'gbif_species_match_',
    VERNACULAR: 'gbif_vernacular_',
    OCCURRENCE: 'gbif_occurrence_',
    IMAGES: 'gbif_images_'
};

// Helper function to get cache entry
const getCache = (prefix, key) => {
    const cacheKey = `${prefix}${key}`;
    try {
        const cached = localStorage.getItem(cacheKey);
        if (!cached) return null;

        const { timestamp, data } = JSON.parse(cached);
        const isExpired = Date.now() - timestamp > 5 * 60 * 1000; // 5 minutes

        return isExpired ? null : data;
    } catch (e) {
        console.error('Cache read error:', e);
        return null;
    }
};

// Helper function to set cache entry
const setCache = (prefix, key, data) => {
    const cacheKey = `${prefix}${key}`;
    try {
        const cacheValue = {
            timestamp: Date.now(),
            data
        };
        localStorage.setItem(cacheKey, JSON.stringify(cacheValue));
    } catch (e) {
        console.error('Cache write error:', e);
    }
};

// Clean up expired cache entries (run this periodically)
export const cleanExpiredCache = () => {
    Object.keys(localStorage).forEach(key => {
        if (key.startsWith('gbif_')) {
            try {
                const cached = JSON.parse(localStorage.getItem(key));
                if (Date.now() - cached.timestamp > 5 * 60 * 1000) {
                    localStorage.removeItem(key);
                }
            } catch (e) {
                localStorage.removeItem(key);
            }
        }
    });
};

// Specific cache operations
export const getCachedSpeciesMatch = (organismName) =>
    getCache(CACHE_PREFIX.SPECIES_MATCH, organismName.toLowerCase());

export const setCachedSpeciesMatch = (organismName, data) =>
    setCache(CACHE_PREFIX.SPECIES_MATCH, organismName.toLowerCase(), data);

export const getCachedVernacularNames = (taxonKey) =>
    getCache(CACHE_PREFIX.VERNACULAR, taxonKey);

export const setCachedVernacularNames = (taxonKey, data) =>
    setCache(CACHE_PREFIX.VERNACULAR, taxonKey, data);

export const getCachedOccurrence = (taxonKey, country) =>
    getCache(CACHE_PREFIX.OCCURRENCE, `${taxonKey}_${country}`);

export const setCachedOccurrence = (taxonKey, country, data) =>
    setCache(CACHE_PREFIX.OCCURRENCE, `${taxonKey}_${country}`, data);

export const getCachedImages = (taxonKey) =>
    getCache(CACHE_PREFIX.IMAGES, taxonKey);

export const setCachedImages = (taxonKey, data) =>
    setCache(CACHE_PREFIX.IMAGES, taxonKey, data);