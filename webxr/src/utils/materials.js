// Runtime material definitions for semantic categories
export const MATERIALS = {
    structure: {
        walls: { color: 0x9e9e9e, opacity: 0.35, metalness: 0.1, roughness: 0.7 },
        slabs: { color: 0xb0bec5, opacity: 0.25, metalness: 0.05, roughness: 0.8 },
        columns: { color: 0x757575, opacity: 0.45, metalness: 0.2, roughness: 0.6 },
        beams: { color: 0x8d6e63, opacity: 0.4, metalness: 0.1, roughness: 0.7 }
    },
    openings: {
        doors: { color: 0xff9800, opacity: 1.0, metalness: 0.3, roughness: 0.4 },
        windows: { color: 0x00bcd4, opacity: 0.6, metalness: 0.9, roughness: 0.2 }
    },
    circulation: {
        stairs: { color: 0xffc107, opacity: 1.0, metalness: 0.2, roughness: 0.5 },
        railings: { color: 0xffffff, opacity: 1.0, metalness: 0.8, roughness: 0.3 }
    },
    mep: {
        terminals: { color: 0x2196f3, opacity: 1.0, metalness: 0.4, roughness: 0.5 },
        controllers: { color: 0x4caf50, opacity: 1.0, metalness: 0.3, roughness: 0.6 }
    }
};

// Apply material based on filename pattern
export function getMaterialForFile(filename) {
    if (filename.includes('structure')) return MATERIALS.structure;
    if (filename.includes('openings')) return MATERIALS.openings;
    if (filename.includes('circulation')) return MATERIALS.circulation;
    if (filename.includes('mep')) return MATERIALS.mep;
    return { default: { color: 0xcccccc, opacity: 0.8 } };
}