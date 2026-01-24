export interface BirdDetection {
    id: number;
    timestamp: string;
    lat: number | null;
    lon: number | null;
    species: string;
    confidence: number;
    audio_url: string;
    single_audio_url: string;
    image_url: string;
    single_image_url: string;
    bird_photo_url: string | null;
}

export interface SpeciesInfo {
    name: string;
    detection_count: number;
    avg_confidence: number;
    last_seen: string;
    first_seen: string;
    image_url: string | null;
    description: string | null;
    region: string | null;
    scientific_name: string | null;
    habitat: string | null;
    conservation_status: string | null;
}
