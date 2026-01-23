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
}
