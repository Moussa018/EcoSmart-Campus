import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  FlashOn as EnergyIcon,
  Warning as AlertIcon,
  EmojiEvents as TrophyIcon,
  Business as BuildingIcon,
  Send as SendIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { apiClient, MOCK_BUILDINGS, MOCK_ALERTS } from '../mocks/apiMock';

export default function GestionnaireView() {
  const [buildings, setBuildings] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [question, setQuestion] = useState('Quel bâtiment a le plus consommé la semaine dernière ?');
  const [assistantResponse, setAssistantResponse] = useState(null);
  const [loadingAssistant, setLoadingAssistant] = useState(false);

  useEffect(() => {
    apiClient.getBuildings().then(setBuildings);
    apiClient.getAlerts().then(setAlerts);
  }, []);

  const handleAskAssistant = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoadingAssistant(true);
    const res = await apiClient.askAssistant(question);
    setAssistantResponse(res);
    setLoadingAssistant(false);
  };

  const totalConso = buildings.reduce((acc, b) => acc + (b.consommation_actuelle || 50), 0);

  return (
    <Box>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        Tableau de bord Gestionnaire · Vue synthétique (Sprint 1)
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Supervision globale du campus, suivi temps réel Énergie et assistant IA intégré.
      </Typography>

      {/* Cartes d'indicateurs clés */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2, borderRadius: 2 }}>
            <Box sx={{ p: 1.5, bgcolor: '#e8f5e9', borderRadius: 2 }}>
              <EnergyIcon sx={{ color: '#2e7d32', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Puissance instantanée
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {totalConso.toFixed(1)} kW
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2, borderRadius: 2 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffebee', borderRadius: 2 }}>
              <AlertIcon sx={{ color: '#d32f2f', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Alertes actives
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {alerts.filter((a) => a.statut === 'ouverte').length}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2, borderRadius: 2 }}>
            <Box sx={{ p: 1.5, bgcolor: '#e3f2fd', borderRadius: 2 }}>
              <BuildingIcon sx={{ color: '#1976d2', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Bâtiments raccordés
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {buildings.length}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2, borderRadius: 2 }}>
            <Box sx={{ p: 1.5, bgcolor: '#fff3e0', borderRadius: 2 }}>
              <TrophyIcon sx={{ color: '#ed6c02', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Éco-score moyen campus
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                71 / 100
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Liste des Bâtiments */}
        <Grid item xs={12} md={7}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Consommation et état des bâtiments
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Bâtiment</TableCell>
                      <TableCell>Zone</TableCell>
                      <TableCell align="right">Surface (m²)</TableCell>
                      <TableCell align="right">Conso actuelle</TableCell>
                      <TableCell align="center">Éco-score</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {buildings.map((b) => (
                      <TableRow key={b.id}>
                        <TableCell fontWeight="medium">{b.nom}</TableCell>
                        <TableCell>{b.zone}</TableCell>
                        <TableCell align="right">{b.surface}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', color: '#1b5e20' }}>
                          {b.consommation_actuelle} kW
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${b.eco_score}/100`}
                            size="small"
                            color={b.eco_score >= 70 ? 'success' : 'warning'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Prototype Assistant LangChain EcoSmart (T09) */}
        <Grid item xs={12} md={5}>
          <Card sx={{ borderRadius: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, bgcolor: '#1b5e20', color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
              <BotIcon />
              <Typography variant="subtitle1" fontWeight="bold">
                Assistant EcoSmart (Sprint 1 - T09)
              </Typography>
            </Box>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1.5 }}>
                Posez une question en langage naturel sur les consommations du campus.
              </Typography>

              <Box sx={{ flexGrow: 1, minHeight: 180, bgcolor: '#f9fbe7', p: 2, borderRadius: 2, mb: 2 }}>
                {assistantResponse ? (
                  <Box>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                      {assistantResponse.reponse}
                    </Typography>
                    {assistantResponse.outils_appeles && assistantResponse.outils_appeles.length > 0 && (
                      <Box sx={{ mt: 2, pt: 1.5, borderTop: '1px dashed #c5e1a5' }}>
                        <Typography variant="caption" color="text.secondary" fontWeight="bold">
                          Outils appelés :
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                          {assistantResponse.outils_appeles.map((t, idx) => (
                            <Chip key={idx} label={t.outil} size="small" variant="outlined" color="success" />
                          ))}
                        </Box>
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                          Latence : {assistantResponse.duree_ms} ms · Modèle : {assistantResponse.modele}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    Exemple de question : « Quel bâtiment a le plus consommé la semaine dernière ? »
                  </Typography>
                )}
              </Box>

              <form onSubmit={handleAskAssistant} style={{ display: 'flex', gap: 8 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Posez votre question..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  disabled={loadingAssistant}
                />
                <Button
                  type="submit"
                  variant="contained"
                  color="success"
                  disabled={loadingAssistant}
                  endIcon={loadingAssistant ? <CircularProgress size={18} color="inherit" /> : <SendIcon />}
                >
                  Envoyer
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
