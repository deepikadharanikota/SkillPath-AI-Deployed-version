import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  UploadCloud, 
  CheckCircle, 
  RefreshCw, 
  Sparkles, 
  ArrowRight,
  AlertCircle,
  FolderOpen
} from 'lucide-react';
import { api } from '../api';
import { ROLE_CATEGORIES } from '../rolesConfig';

import { useQuery, useQueryClient } from '@tanstack/react-query';

export default function ResumeUpload() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: resumeData, isLoading: loading } = useQuery({
    queryKey: ['resume'],
    queryFn: api.getResume,
    staleTime: 5 * 60 * 1000,
  });

  const [targetRole, setTargetRole] = useState('ML Engineer');
  const [selectedFile, setSelectedFile] = useState(null);
  const [pastedText, setPastedText] = useState('');
  const [useTextInput, setUseTextInput] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (resumeData?.target_role) {
      setTargetRole(resumeData.target_role);
    }
  }, [resumeData]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    if (!selectedFile && !pastedText.trim()) {
      setError('Please select a PDF/DOCX file or paste your resume text.');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append('file', selectedFile);
      }
      if (pastedText.trim()) {
        formData.append('resume_text', pastedText.trim());
      }
      formData.append('target_role', targetRole);

      const result = await api.uploadResumeFile(formData);
      setSuccessMsg(result.message || 'Resume uploaded and skills analyzed successfully!');
      setSelectedFile(null);
      setPastedText('');
      queryClient.invalidateQueries({ queryKey: ['resume'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      queryClient.invalidateQueries({ queryKey: ['learningResume'] });
      queryClient.invalidateQueries({ queryKey: ['skillGap'] });
    } catch (err) {
      setError(err.message || 'Failed to upload resume. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleTargetRoleChange = async (newRole) => {
    setTargetRole(newRole);
    try {
      await api.updateTargetRole(newRole);
      queryClient.invalidateQueries({ queryKey: ['resume'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      queryClient.invalidateQueries({ queryKey: ['learningResume'] });
      queryClient.invalidateQueries({ queryKey: ['skillGap'] });
    } catch (err) {
      console.error('Role update error:', err);
    }
  };

  if (loading && !resumeData) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '50vh', gap: '14px' }}>
        <RefreshCw size={32} color="#818cf8" style={{ animation: 'spin 1s linear infinite' }} />
        <span style={{ color: 'var(--text-muted)' }}>Loading resume details...</span>
      </div>
    );
  }

  const hasResume = resumeData?.has_resume;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.4rem' }}>Resume & Skill Intelligence</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Upload your resume to extract skills, analyze gaps for your target role, and power your adaptive curriculum.
        </p>
      </div>

      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          padding: '1rem',
          borderRadius: '12px',
          color: '#fca5a5',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div style={{
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          padding: '1rem',
          borderRadius: '12px',
          color: '#6ee7b7',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <CheckCircle size={20} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Target Role Selector Card */}
      <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '4px' }}>Target Career Role</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem' }}>
            SkillPath AI will benchmark your extracted skills against this target role.
          </p>
        </div>
        <select
          value={targetRole}
          onChange={(e) => handleTargetRoleChange(e.target.value)}
          className="input-field"
          style={{ width: 'auto', minWidth: '280px', backgroundColor: '#13182b', cursor: 'pointer', fontWeight: '600' }}
        >
          {ROLE_CATEGORIES.map((cat) => (
            <optgroup key={cat.name} label={`${cat.icon} ${cat.name}`}>
              {cat.roles.map((r) => (
                <option key={r.name} value={r.name}>
                  {r.name}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>

      {/* ── Active Resume Card (One User = One Resume) ── */}
      {hasResume && (
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <FileText size={24} color="#818cf8" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', marginBottom: '2px' }}>{resumeData.resume?.filename}</h3>
                <span style={{ fontSize: '0.84rem', color: 'var(--text-dim)' }}>
                  Uploaded: {resumeData.resume?.uploaded_at} &nbsp;|&nbsp; {resumeData.extracted_skills?.length || 0} Skills Extracted
                </span>
              </div>
            </div>

            <button onClick={() => navigate('/skill-gap')} className="btn-primary">
              <span>View Skill Gap Analysis</span>
              <ArrowRight size={16} />
            </button>
          </div>

          {/* Categorized Extracted Skills */}
          <div>
            <h4 style={{ fontSize: '0.95rem', color: 'var(--text-muted)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Extracted Technical Skills by Category:
            </h4>

            {resumeData.categorized_skills && Object.keys(resumeData.categorized_skills).length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                {Object.entries(resumeData.categorized_skills).map(([cat, skList]) => (
                  <div
                    key={cat}
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '10px',
                      padding: '1rem'
                    }}
                  >
                    <div style={{ fontSize: '0.86rem', fontWeight: '600', color: '#a5b4fc', marginBottom: '8px' }}>
                      {cat}
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {skList.map((sk) => (
                        <span key={sk} className="badge badge-indigo" style={{ fontSize: '0.78rem' }}>
                          • {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {resumeData.extracted_skills?.map((sk) => (
                  <span key={sk} className="badge badge-indigo">
                    • {sk}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Re-upload / Upload Dropzone Card ── */}
      <div className="glass-card" style={{ padding: '2rem' }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '4px' }}>
            {hasResume ? 'Replace / Re-upload Resume' : 'Upload Your Resume'}
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            {hasResume 
              ? 'Re-uploading will automatically update your active resume and recalculate all skills and curriculum gaps.' 
              : 'Support for PDF or DOCX format. Text will be parsed securely on the server.'}
          </p>
        </div>

        {/* Input Toggle */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '1.25rem' }}>
          <button
            type="button"
            onClick={() => setUseTextInput(false)}
            className={!useTextInput ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '8px 16px', fontSize: '0.86rem' }}
          >
            <FolderOpen size={16} />
            <span>Upload File (PDF / DOCX)</span>
          </button>
          <button
            type="button"
            onClick={() => setUseTextInput(true)}
            className={useTextInput ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '8px 16px', fontSize: '0.86rem' }}
          >
            <span>Paste Resume Text</span>
          </button>
        </div>

        <form onSubmit={handleUploadSubmit}>
          {!useTextInput ? (
            <div
              style={{
                border: '2px dashed var(--border-color)',
                borderRadius: '16px',
                padding: '2.5rem 1.5rem',
                textAlign: 'center',
                backgroundColor: selectedFile ? 'rgba(99, 102, 241, 0.05)' : 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                marginBottom: '1.25rem',
                position: 'relative'
              }}
              onClick={() => document.getElementById('resume-file-input').click()}
            >
              <input
                id="resume-file-input"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <UploadCloud size={44} color={selectedFile ? '#818cf8' : '#9ca3af'} style={{ margin: '0 auto 12px' }} />
              {selectedFile ? (
                <div>
                  <p style={{ fontWeight: '600', color: '#fff', fontSize: '1.05rem', marginBottom: '4px' }}>
                    {selectedFile.name}
                  </p>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {(selectedFile.size / 1024).toFixed(1)} KB — Click to change file
                  </span>
                </div>
              ) : (
                <div>
                  <p style={{ fontWeight: '600', color: '#fff', fontSize: '1rem', marginBottom: '4px' }}>
                    Click or drag & drop your resume file here
                  </p>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                    PDF, DOCX up to 10MB
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div style={{ marginBottom: '1.25rem' }}>
              <textarea
                rows={8}
                className="input-field"
                placeholder="Paste the plain text of your resume here..."
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={uploading || (!selectedFile && !pastedText.trim())}
            className="btn-primary"
            style={{ padding: '12px 24px', fontSize: '0.95rem' }}
          >
            {uploading ? (
              <>
                <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                <span>Extracting Skills & Analyzing Gaps...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>{hasResume ? 'Re-upload & Extract New Skills' : 'Analyze Resume'}</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
