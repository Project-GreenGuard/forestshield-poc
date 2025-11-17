const API_BASE_URL = "http://localhost:5001/api";

/**
 * Fetches all active wildfires from the API
 * @returns {Promise<Array>} Array of fire objects
 */
export const getFires = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/fires`);
    if (!response.ok) {
      throw new Error("Failed to fetch fires");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching fires:", error);
    return [];
  }
};

/**
 * Fetches summary statistics from the API
 * @returns {Promise<Object>} Summary object with stats
 */
export const getSummary = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/summary`);
    if (!response.ok) {
      throw new Error("Failed to fetch summary");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching summary:", error);
    return {
      averageTemperature: 0,
      highRiskCount: 0,
      timestamp: new Date().toISOString(),
    };
  }
};

/**
 * Fetches current temperature from the API
 * @returns {Promise<number|null>} Current temperature value
 */
export const getTemperature = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/temperature`);
    if (!response.ok) {
      throw new Error("Failed to fetch temperature");
    }
    const data = await response.json();
    return data.temperature;
  } catch (error) {
    console.error("Error fetching temperature:", error);
    return null;
  }
};
