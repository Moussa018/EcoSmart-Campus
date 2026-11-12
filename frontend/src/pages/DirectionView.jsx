import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Divider,
} from '@mui/material';
import {
  Assessment as KpiIcon,
  TrendingDown as SavingIcon,
  Co2 as Co2Icon,
  AccountBalance as DirectionIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { apiClient } from '../mocks/apiMock';

export default function DirectionView() {
  const [executiveSummary, setExecutiveSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateSummary = async () => {
    setLoading(true);
    const res = await apiClient.askAssistant(
      'Donne un résumé exécutif des consommations et des économies potentielles pour la direction.'
    );
    setExecutiveSummary(res);
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        Tableau de bord Stratégique · Direction (Sprint 1 - T07)
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Indicateurs clés de performance, atteinte des objectifs et aide à la décision.
      </Typography>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2.5, bgcolor: '#e8f5e9', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
              <SavingIcon color="success" />
              <Typography variant="subtitle2" fontWeight="bold" color="success.main">
                Économies estimées (Hors cours)
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold">
              20 986 € / an
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Gisement d'extinction nocturne & week-end
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2.5, bgcolor: '#e3f2fd', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
              <Co2Icon color="primary" />
              <Typography variant="subtitle2" fontWeight="bold" color="primary.main">
                Réduction Carbone Potentielle
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold">
              5,25 tonnes CO₂e
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Émissions évitables sur le parc bâtiment
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2.5, bgcolor: '#f3e5f5', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
              <KpiIcon color="secondary" />
              <Typography variant="subtitle2" fontWeight="bold" color="secondary.main">
                Objectif de sobriété campus
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold">
              - 15 %
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Trajectoire 2026-2027 validée
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Suivi des objectifs par bâtiment (Novembre 2026)
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Bâtiment</TableCell>
                      <TableCell align="right">Cible mensuelle</TableCell>
                      <TableCell align="right">Estimé actuel</TableCell>
                      <TableCell align="center">Statut</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell fontWeight="medium">Bâtiment A - Sciences</TableCell>
                      <TableCell align="right">25 000 kWh</TableCell>
                      <TableCell align="right">23 800 kWh</TableCell>
                      <TableCell align="center">
                        <Chip label="Conforme (-4.8%)" size="small" color="success" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell fontWeight="medium">Bâtiment B - Enseignement</TableCell>
                      <TableCell align="right">28 000 kWh</TableCell>
                      <TableCell align="right">30 200 kWh</TableCell>
                      <TableCell align="center">
                        <Chip label="Dépassement (+7.8%)" size="small" color="error" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell fontWeight="medium">Bâtiment C - Recherche</TableCell>
                      <TableCell align="right">20 000 kWh</TableCell>
                      <TableCell align="right">19 500 kWh</TableCell>
                      <TableCell align="center">
                        <Chip label="Conforme (-2.5%)" size="small" color="success" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell fontWeight="medium">Bâtiment D - Administration</TableCell>
                      <TableCell align="right">8 000 kWh</TableCell>
                      <TableCell align="right">7 100 kWh</TableCell>
                      <TableCell align="center">
                        <Chip label="Très bon (-11.2%)" size="small" color="success" />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                <BotIcon color="primary" />
                <Typography variant="subtitle1" fontWeight="bold">
                  Bilan Décisionnel IA (T09 / RF22)
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Générez instantanément une note de synthèse pour la direction.
              </Typography>

              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleGenerateSummary}
                disabled={loading}
                sx={{ mb: 2, textTransform: 'none' }}
              >
                {loading ? 'Génération de la note...' : 'Rédiger la note de synthèse'}
              </Button>

              {executiveSummary && (
                <Paper sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                    {executiveSummary.reponse}
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
