// ✅ 1. src/components/TestGenerator.tsx
// =============================
import React, { useState, FormEvent } from "react";
import {
  TextField,
  Button,
  Typography,
  CircularProgress,
  Box,
  Paper,
  MenuItem,
  Checkbox,
  FormControlLabel,
} from "@mui/material";
import axios from "axios";
import TestResultsViewer from "./TestResultsViewer";
import TestHistoryViewer from "./TestHistoryViewer";

interface TestRunResponse {
  output: string;
  error?: string;
  status: "success" | "error";
}

interface Props {
  licenseToken: string;
}

const TestGenerator: React.FC<Props> = ({ licenseToken }) => {
  const [repoUrl, setRepoUrl] = useState<string>("");
  const [language, setLanguage] = useState<string>("python");
  const [filePath, setFilePath] = useState<string>("");
  const [folderFilter, setFolderFilter] = useState<string>("");
  const [testType, setTestType] = useState<string>("auto");
  const [dryRun, setDryRun] = useState<boolean>(false);
  const [result, setResult] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<TestRunResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [testsSaved, setTestsSaved] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setTestResults(null);
    setTestsSaved(false);

    try {
      const response = await axios.post("http://localhost:8000/api/tests/generate", {
        repo_url: repoUrl,
        language,
        file_path: filePath,
        folder_filter: folderFilter,
        dry_run: dryRun,
        test_type: testType,
        license_token: licenseToken,
      });

      setResult(response.data.generated_test_code);
      if (!dryRun) {
        setTestsSaved(true);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadZip = async () => {
    if (!repoUrl) return;

    const repoNameRaw = repoUrl.trim().split("/").pop()?.replace(".git", "") || "";
    const repoName = repoNameRaw.replace(/-/g, "_");

    const zipUrl = `http://localhost:8000/api/tests/download/${repoName}`;

    try {
      const response = await axios.get(zipUrl, {
        responseType: "blob",
      });

      const blob = new Blob([response.data], { type: "application/zip" });
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `${repoName}_tests.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert("❌ Failed to download ZIP: " + (err.response?.data?.detail || "Unknown error."));
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        ⚙️ Generate AI Test Cases
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <TextField
          label="Repository URL"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          required
          fullWidth
        />

        <TextField select label="Language" value={language} onChange={(e) => setLanguage(e.target.value)} fullWidth>
          <MenuItem value="python">Python</MenuItem>
          <MenuItem value="java">Java</MenuItem>
          <MenuItem value="javascript">JavaScript</MenuItem>
          <MenuItem value="typescript">TypeScript</MenuItem>
        </TextField>

        <TextField
          label="File Path (Optional)"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          placeholder="e.g. src/utils/helper.py"
          fullWidth
        />

        <TextField
          label="Folder Filter (Optional)"
          value={folderFilter}
          onChange={(e) => setFolderFilter(e.target.value)}
          placeholder="e.g. src/controllers/"
          fullWidth
        />

        <TextField select label="Test Type" value={testType} onChange={(e) => setTestType(e.target.value)} fullWidth>
          <MenuItem value="auto">Auto (Smart)</MenuItem>
          <MenuItem value="unit">Unit</MenuItem>
          <MenuItem value="ui">UI / End-to-End</MenuItem>
        </TextField>

        <FormControlLabel
          control={<Checkbox checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} />}
          label="Dry Run (Don't save tests)"
        />

        <Button type="submit" variant="contained" color="secondary" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : "Generate"}
        </Button>

        {testsSaved && (
          <Button variant="outlined" color="success" onClick={handleDownloadZip}>
            📦 Download All Tests
          </Button>
        )}
      </Box>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}

      {result && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6">🧪 Generated Test Code:</Typography>
          <Paper
            variant="outlined"
            sx={{
              mt: 1,
              p: 2,
              whiteSpace: "pre-wrap",
              fontFamily: "monospace",
              maxHeight: "60vh",
              overflowY: "auto",
            }}
          >
            {result}
          </Paper>
        </Box>
      )}

      {testResults && <TestResultsViewer results={testResults} />}

      {repoUrl && (
        <Box sx={{ mt: 4 }}>
          <TestHistoryViewer
            repo={repoUrl.trim().replace(/\/+$/, "").split("/").pop()?.replace(/\.git$/, "").replace(/-/g, "_") || ""}
          />
        </Box>
      )}
    </Paper>
  );
};

export default TestGenerator;