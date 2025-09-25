import React, { useEffect, useState } from "react";
import {
  Paper,
  Typography,
  CircularProgress,
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemText,
} from "@mui/material";
import axios from "axios";

interface TestHistoryViewerProps {
  repo: string;
}

const TestHistoryViewer: React.FC<TestHistoryViewerProps> = ({ repo }) => {
  const [files, setFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [fileContent, setFileContent] = useState<string>("");
  const [loadingFiles, setLoadingFiles] = useState<boolean>(true);
  const [loadingContent, setLoadingContent] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchFileList = async () => {
      try {
        const response = await axios.get<{ files: string[] }>(
          `http://localhost:8000/api/history/${repo}`
        );
        setFiles(response.data.files || []);
      } catch (err) {
        setError("⚠️ Failed to load file list.");
      } finally {
        setLoadingFiles(false);
      }
    };

    if (repo) fetchFileList();
  }, [repo]);

  const handleFileClick = async (filename: string) => {
    setSelectedFile(filename);
    setFileContent("");
    setLoadingContent(true);

    try {
      const res = await axios.get<{ content: string }>(
        `http://localhost:8000/api/history/${repo}/file/${filename}`
      );
      setFileContent(res.data.content);
    } catch (err) {
      setFileContent("⚠️ Failed to load file content.");
    } finally {
      setLoadingContent(false);
    }
  };

  if (loadingFiles) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!files.length)
    return <Typography>No test history found for {repo}</Typography>;

  return (
    <Paper sx={{ mt: 4, p: 3 }}>
      <Typography variant="h6" gutterBottom>
        🗂️ Test History for: {repo}
      </Typography>
      <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
        {/* File list */}
        <Paper
          variant="outlined"
          sx={{ width: "30%", maxHeight: 300, overflowY: "auto" }}
        >
          <List dense>
            {files.map((filename, idx) => (
              <ListItemButton
                key={idx}
                selected={filename === selectedFile}
                onClick={() => handleFileClick(filename)}
              >
                <ListItemText primary={filename} />
              </ListItemButton>
            ))}
          </List>
        </Paper>

        {/* File content */}
        <Paper
          variant="outlined"
          sx={{
            width: "70%",
            p: 2,
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            maxHeight: 300,
            overflowY: "auto",
          }}
        >
          {loadingContent ? (
            <CircularProgress size={20} />
          ) : selectedFile ? (
            <>
              <Typography variant="subtitle2">📄 {selectedFile}</Typography>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body2">{fileContent}</Typography>
            </>
          ) : (
            <Typography variant="body2" color="textSecondary">
              🔍 Select a test file to view content.
            </Typography>
          )}
        </Paper>
      </Box>
    </Paper>
  );
};

export default TestHistoryViewer;