const API_URL = import.meta.env.VITE_API_URL as string;

export const getAreas = async () => {
  try {
    const response = await fetch(`${API_URL}/get_areas`);
    if (!response.ok) {
      throw new Error('Failed to fetch areas');
    }
    return await response.json();
  } catch (error) {
    return [];
  }
}