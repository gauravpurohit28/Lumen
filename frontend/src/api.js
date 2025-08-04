import axios from 'axios';

const API_BASE_URL = 'https://lumen-kxdv.onrender.com';

export const captureImage = async () => {
  return axios.post(`${API_BASE_URL}/api/capture`);
};

export const askQuestion = async (question) => {
  return axios.post(`${API_BASE_URL}/api/question`, { question });
};

export const askQuestionAudio = async (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'question.webm');
  return axios.post(`${API_BASE_URL}/api/question-audio`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getHistory = async () => {
  return axios.get(`${API_BASE_URL}/api/history`);
};

export const speakText = async (text) => {
  const response = await axios.post(`${API_BASE_URL}/api/tts`, { text }, {
    responseType: 'blob' // Important for handling audio blob
  });
  return response.data;
}; 