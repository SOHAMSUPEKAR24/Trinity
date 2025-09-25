import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Chip,
  Divider,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";

interface TestResults {
  status: "success" | "error";
  output?: string;
  error?: string;
}

interface TestResultsViewerProps {
  results: TestResults;
}

const TestResultsViewer: React.FC<TestResultsViewerProps> = ({ results }) => {
  const [tab, setTab] = useState<number>(0);

  if (!results) return null;

  const isSuccess = results.status === "success";

  return (
    <Paper elevation={3} sx={{ mt: 4, p: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h6">🧪 Test Results</Typography>
        <Chip
          icon={isSuccess ? <CheckCircleIcon color="success" /> : <ErrorIcon color="error" />}
          label={isSuccess ? "Success" : "Failed"}
          color={isSuccess ? "success" : "error"}
          variant="outlined"
        />
      </Box>

      <Divider sx={{ mb: 2 }} />

      <Tabs value={tab} onChange={(_, newTab: number) => setTab(newTab)} sx={{ mb: 2 }}>
        <Tab label="Stdout" />
        <Tab label="Stderr" />
      </Tabs>

      <Box
        sx={{
          whiteSpace: "pre-wrap",
          fontFamily: "monospace",
          backgroundColor: "#f9f9f9",
          border: "1px solid #ddd",
          borderRadius: 2,
          p: 2,
          maxHeight: 400,
          overflowY: "auto",
        }}
      >
        {tab === 0
          ? results.output || "No stdout output."
          : results.error || "No stderr output."}
      </Box>
    </Paper>
  );
};

export default TestResultsViewer;