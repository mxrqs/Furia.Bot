const express = require('express');
const app = express();

// A variável de ambiente PORT definida pelo Render será usada
const port = process.env.PORT || 3000;  // Usa o valor de PORT ou 3000 como fallback

const furiaGames = [
  { team1: "FURIA", team2: "The MongolZ", event: "PGL Bucharest 2025", date: "2025-04-12", result: "0 - 2", type: "finished" },
  { team1: "FURIA", team2: "Virtus.pro", event: "PGL Bucharest 2025", date: "2025-04-13", result: "0 - 2", type: "finished" },
  { team1: "FURIA", team2: "Complexity", event: "PGL Bucharest 2025", date: "2025-04-14", result: "1 - 2", type: "finished" },
  { team1: "FURIA", team2: "Betclic", event: "PGL Bucharest 2025", date: "2025-04-14", result: "2 - 0", type: "finished" },
];

// Rotas
app.get('/api/findall', (req, res) => {
  res.json(furiaGames);
});

app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});
