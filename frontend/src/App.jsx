import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fileInfo, setFileInfo] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setError("");
    setAnalysis("");
    setFileInfo(null);

    if (!selectedFile) {
      setFile(null);
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setError("Please select a PDF file.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const analyzePDF = async () => {
    if (!file) {
      setError("Please select a PDF file first.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis("");
    setFileInfo(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/analyze-pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to analyze the PDF.");
      }

      if (!data.success) {
        throw new Error("PDF analysis failed.");
      }

      setAnalysis(data.analysis);

      setFileInfo({
        filename: data.filename,
        pages: data.pages,
        characters: data.extracted_characters,
      });
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const formatAnalysis = (text) => {
    return text.split("\n").map((line, index) => {
      if (line.trim() === "") {
        return <div className="analysis-space" key={index} />;
      }

      if (
        line === "LEGAL DOCUMENT ANALYSIS" ||
        line === "KEY CLAUSES" ||
        line === "SUMMARY:"
      ) {
        return (
          <h2 className="analysis-heading" key={index}>
            {line.replace(":", "")}
          </h2>
        );
      }

      return (
        <p className="analysis-line" key={index}>
          {line}
        </p>
      );
    });
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">⚖</div>

          <div>
            <h1>Legal Document Analyzer</h1>
            <p>AI-powered contract understanding</p>
          </div>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <h2>Analyze Your Legal Contract</h2>

          <p>
            Upload a commercial legal document and let local AI extract
            important contractual information and clauses.
          </p>
        </section>

        <section className="upload-card">
          <div className="upload-icon">📄</div>

          <h3>Upload PDF Contract</h3>

          <p className="upload-description">
            Select a PDF containing your legal agreement.
          </p>

          <label className="file-button">
            Choose PDF
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              hidden
            />
          </label>

          {file && (
            <div className="selected-file">
              <span>📄</span>

              <div>
                <strong>{file.name}</strong>
                <small>
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </small>
              </div>
            </div>
          )}

          {error && <div className="error">{error}</div>}

          <button
            className="analyze-button"
            onClick={analyzePDF}
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing Contract...
              </>
            ) : (
              "Analyze Contract"
            )}
          </button>
        </section>

        {fileInfo && (
          <section className="file-info">
            <div>
              <span>📄</span>
              <strong>{fileInfo.filename}</strong>
            </div>

            <div>
              <span>Pages</span>
              <strong>{fileInfo.pages}</strong>
            </div>

            <div>
              <span>Extracted Characters</span>
              <strong>{fileInfo.characters}</strong>
            </div>
          </section>
        )}

        {loading && (
          <section className="loading-card">
            <div className="large-spinner"></div>

            <h3>Analyzing your contract...</h3>

            <p>
              Extracting the document text and analyzing it with
              Llama 3.2.
            </p>

            <small>
              This may take a little while for longer contracts.
            </small>
          </section>
        )}

        {analysis && !loading && (
          <section className="result-card">
            <div className="result-header">
              <div>
                <span className="success-icon">✓</span>
              </div>

              <div>
                <h2>Legal Document Analysis</h2>
                <p>
                  AI-generated information extracted from your document.
                </p>
              </div>
            </div>

            <div className="analysis-content">
              {formatAnalysis(analysis)}
            </div>

            <div className="disclaimer">
              <strong>Important:</strong> This analysis is generated by AI
              for informational purposes only and is not legal advice.
            </div>
          </section>
        )}

        <section className="features">
          <div className="feature-card">
            <div className="feature-icon">📄</div>
            <h3>Contract Understanding</h3>
            <p>
              Extracts important information from commercial legal
              contracts.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>41 Legal Categories</h3>
            <p>
              Based on the Contract Understanding Atticus Dataset
              categories.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Local AI</h3>
            <p>
              Analysis runs locally using Ollama and Llama 3.2.
            </p>
          </div>
        </section>
      </main>

      <footer>
        <p>Automated Legal Document Analyzer</p>
        <p>Powered by FastAPI + Ollama + Llama 3.2</p>
      </footer>
    </div>
  );
}

export default App;
