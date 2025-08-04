import React, { useState, useRef, useEffect } from 'react';
import { Container, Typography, Button, CircularProgress, Box, Grid, Card, CardContent, CardMedia, CardActionArea, Tooltip, Divider } from '@mui/material';
import HearingIcon from '@mui/icons-material/Hearing';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import ImageIcon from '@mui/icons-material/Image';
import { captureImage, askQuestionAudio, getHistory, speakText } from './api'; // Import API functions
import axios from 'axios';

function App() {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('idle'); // idle, capturing, waiting_for_question, recording, uploading, answering
  const [errorMsg, setErrorMsg] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [imageCaptured, setImageCaptured] = useState(false);
  const [description, setDescription] = useState('');
  const [answer, setAnswer] = useState('');
  const [imageB64, setImageB64] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [history, setHistory] = useState([]);

  const startRecording = () => {
    setIsRecording(true);
    setStep('recording');
    setErrorMsg('');
    audioChunksRef.current = [];
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new window.MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            audioChunksRef.current.push(e.data);
          }
        };
        mediaRecorder.onstop = () => {
          setIsRecording(false);
          setStep('uploading');
          handleAudioUpload();
        };
        mediaRecorder.start();
        // No extra prompt, just record
        setTimeout(() => {
          if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
          }
        }, 6000); // Record for 6 seconds max
      })
      .catch(err => {
        setErrorMsg('Microphone access denied or not available.');
        setIsRecording(false);
        setStep('waiting_for_question');
      });
  };

  const fetchHistory = async () => {
    try {
      const res = await getHistory(); // Use getHistory from api.js
      setHistory(res.data.history || []);
    } catch (err) {
      // ignore for now
    }
  };

  useEffect(() => { fetchHistory(); }, []);

  const handleAudioUpload = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // 1. Upload audio for question
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', audioBlob, 'question.webm');
      const ans = await askQuestionAudio(audioBlob); // Use askQuestionAudio from api.js
      setAnswer(ans.answer);
      speakText(ans.answer);
      setStep('waiting_for_question');
      await fetchHistory();
    } catch (err) {
      setErrorMsg('Sorry, something went wrong.');
      speakText('Sorry, something went wrong.');
      setStep('waiting_for_question');
    }
    setLoading(false);
  };

  const handleButtonClick = async () => {
    setErrorMsg('');
    setAnswer('');
    if (!imageCaptured) {
      setLoading(true);
      setStep('capturing');
      try {
        // 1. Capture image and get description
        const captureRes = await captureImage(); // Use captureImage from api.js
        const desc = captureRes.data.description;
        const imgB64 = captureRes.data.image_b64;
        setDescription(desc);
        setImageB64(imgB64);
        speakText(desc);
        setImageCaptured(true);
        setStep('waiting_for_question');
        await fetchHistory();
      } catch (err) {
        setErrorMsg('Sorry, something went wrong.');
        speakText('Sorry, something went wrong.');
        setStep('idle');
      }
      setLoading(false);
    } else {
      // Already have an image, just ask a new question
      setStep('waiting_for_question');
      setTimeout(() => {
        startRecording();
      }, 500);
    }
  };

  const handleNewImage = () => {
    setImageCaptured(false);
    setDescription('');
    setImageB64('');
    setAnswer('');
    setStep('idle');
    setErrorMsg('');
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography variant="h3" align="center" fontWeight={700} color="primary" gutterBottom>
        Lumen: Visual Q&A for the Blind
      </Typography>
      <Typography variant="body1" align="center" sx={{ mb: 4 }}>
        Press the button below to capture an image and hear its description. Then ask your question about what is in front of you. The answer will be spoken aloud. Press the button again to ask more questions about the same image, or click "New Image" to capture a new image.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        size="large"
        startIcon={<HearingIcon />}
        onClick={handleButtonClick}
        disabled={loading || isRecording}
        sx={{ fontSize: 24, py: 3, px: 5, borderRadius: 3, mb: 2, boxShadow: 3 }}
        aria-label="Ask about what is in front of me"
      >
        {loading || isRecording ? <CircularProgress size={32} color="inherit" /> : (imageCaptured ? "Ask about this image" : "What's in front of me?")}
      </Button>
      {imageCaptured && (
        <Button
          variant="outlined"
          color="secondary"
          onClick={handleNewImage}
          sx={{ mb: 2 }}
        >
          New Image
        </Button>
      )}
      {imageCaptured && imageB64 && (
        <Box sx={{ mt: 2, mb: 2 }}>
          <img src={`data:image/jpeg;base64,${imageB64}`} alt="Captured scene" style={{ maxWidth: '100%', borderRadius: 12, boxShadow: '0 4px 24px rgba(0,0,0,0.12)' }} />
        </Box>
      )}
      <Box mt={4} mb={6}>
        {step === 'capturing' && <Typography variant="h6">Capturing image and describing scene...</Typography>}
        {step === 'recording' && <Typography variant="h6">Recording your question... Please speak now.</Typography>}
        {step === 'uploading' && <Typography variant="h6">Processing your question...</Typography>}
        {step === 'answering' && <Typography variant="h6">Answering your question...</Typography>}
        {description && <Typography variant="body1" sx={{ mt: 2 }}><b>Last Description:</b> {description}</Typography>}
        {answer && <Typography variant="body1" sx={{ mt: 2 }}><b>Answer:</b> {answer}</Typography>}
        {errorMsg && <Typography variant="body1" color="error" sx={{ mt: 2 }}>{errorMsg}</Typography>}
      </Box>
      <Divider sx={{ my: 4, width: '100%' }} />
      <Typography variant="h5" align="center" fontWeight={600} color="primary" gutterBottom>
        Recent Visual Q&A
      </Typography>
      <Grid container spacing={3} justifyContent="center" alignItems="stretch" sx={{ mb: 8 }}>
        {history.map((item, idx) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={idx}>
            <Card sx={{ height: '100%', borderRadius: 4, boxShadow: 6, transition: 'transform 0.2s', '&:hover': { transform: 'scale(1.03)' } }}>
              <CardActionArea>
                {item.image_b64 ? (
                  <CardMedia
                    component="img"
                    height="160"
                    image={`data:image/jpeg;base64,${item.image_b64}`}
                    alt="History visual"
                    sx={{ objectFit: 'cover', borderTopLeftRadius: 16, borderTopRightRadius: 16 }}
                  />
                ) : (
                  <Box sx={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.100' }}>
                    <ImageIcon sx={{ fontSize: 48, color: 'grey.400' }} />
                  </Box>
                )}
                <CardContent>
                  <Tooltip title={item.description || ''} arrow>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom noWrap>
                      {item.description || 'No description'}
                    </Typography>
                  </Tooltip>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <QuestionAnswerIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2" color="text.secondary" noWrap>
                      <b>Q:</b> {item.question || <span style={{ color: '#aaa' }}>No question</span>}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ minHeight: 32 }}>
                    <b>A:</b> {item.answer || <span style={{ color: '#aaa' }}>No answer</span>}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default App; 