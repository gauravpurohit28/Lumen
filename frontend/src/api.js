import axios from 'axios';

export const captureImage = async () => {
  return axios.post('/api/capture');
};

export const askQuestion = async (question) => {
  return axios.post('/api/question', { question });
}; 