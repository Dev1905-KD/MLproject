import React, { useState } from 'react';
import { Sparkles, Calculator, BookOpen, Edit3, Award, Lightbulb, Check } from 'lucide-react';
import { predictScore } from '../api';

export default function SinglePredictor() {
  const [formData, setFormData] = useState({
    gender: 'female',
    race_ethnicity: 'group B',
    parental_level_of_education: "bachelor's degree",
    lunch: 'standard',
    test_preparation_course: 'none',
    reading_score: 75,
    writing_score: 72,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const options = {
    gender: [
      { label: 'Female', value: 'female' },
      { label: 'Male', value: 'male' },
    ],
    race_ethnicity: [
      { label: 'Group A', value: 'group A' },
      { label: 'Group B', value: 'group B' },
      { label: 'Group C', value: 'group C' },
      { label: 'Group D', value: 'group D' },
      { label: 'Group E', value: 'group E' },
    ],
    parental_level_of_education: [
      { label: 'Some High School', value: 'some high school' },
      { label: 'High School', value: 'high school' },
      { label: 'Some College', value: 'some college' },
      { label: "Associate's Degree", value: "associate's degree" },
      { label: "Bachelor's Degree", value: "bachelor's degree" },
      { label: "Master's Degree", value: "master's degree" },
    ],
    lunch: [
      { label: 'Standard', value: 'standard' },
      { label: 'Free / Reduced', value: 'free/reduced' },
    ],
    test_preparation_course: [
      { label: 'None', value: 'none' },
      { label: 'Completed', value: 'completed' },
    ],
  };

  const handleSelect = (field, val) => {
    setFormData((prev) => ({ ...prev, [field]: val }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await predictScore(formData);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getGradeClass = (grade) => {
    if (grade === 'A+' || grade === 'A') return 'grade-A-plus';
    if (grade === 'B') return 'grade-B';
    if (grade === 'C') return 'grade-C';
    return 'grade-D';
  };

  return (
    <div className="predictor-grid">
      {/* Input Form */}
      <div className="glass-card form-section">
        <h2 className="form-title">
          <Calculator size={22} color="#6366f1" />
          Student Demographics & Test Scores
        </h2>
        <form onSubmit={handleSubmit}>
          {/* Gender */}
          <div className="form-group">
            <label className="form-label">Gender</label>
            <div className="pill-options">
              {options.gender.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  className={`pill-btn ${formData.gender === opt.value ? 'selected' : ''}`}
                  onClick={() => handleSelect('gender', opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Race/Ethnicity */}
          <div className="form-group">
            <label className="form-label">Race / Ethnicity Group</label>
            <div className="pill-options">
              {options.race_ethnicity.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  className={`pill-btn ${formData.race_ethnicity === opt.value ? 'selected' : ''}`}
                  onClick={() => handleSelect('race_ethnicity', opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Parental Education */}
          <div className="form-group">
            <label className="form-label">Parental Education Level</label>
            <div className="pill-options">
              {options.parental_level_of_education.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  className={`pill-btn ${
                    formData.parental_level_of_education === opt.value ? 'selected' : ''
                  }`}
                  onClick={() => handleSelect('parental_level_of_education', opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Lunch */}
          <div className="form-group">
            <label className="form-label">Lunch Plan Type</label>
            <div className="pill-options">
              {options.lunch.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  className={`pill-btn ${formData.lunch === opt.value ? 'selected' : ''}`}
                  onClick={() => handleSelect('lunch', opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Test Prep */}
          <div className="form-group">
            <label className="form-label">Test Preparation Course</label>
            <div className="pill-options">
              {options.test_preparation_course.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  className={`pill-btn ${
                    formData.test_preparation_course === opt.value ? 'selected' : ''
                  }`}
                  onClick={() => handleSelect('test_preparation_course', opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Reading Score Slider */}
          <div className="form-group">
            <label className="form-label">
              <BookOpen size={16} style={{ display: 'inline', marginRight: 6 }} />
              Reading Score: <span>{formData.reading_score}</span> / 100
            </label>
            <div className="range-container">
              <input
                type="range"
                min="0"
                max="100"
                className="custom-range"
                value={formData.reading_score}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, reading_score: parseInt(e.target.value) }))
                }
              />
              <div className="score-badge">{formData.reading_score}</div>
            </div>
          </div>

          {/* Writing Score Slider */}
          <div className="form-group">
            <label className="form-label">
              <Edit3 size={16} style={{ display: 'inline', marginRight: 6 }} />
              Writing Score: <span>{formData.writing_score}</span> / 100
            </label>
            <div className="range-container">
              <input
                type="range"
                min="0"
                max="100"
                className="custom-range"
                value={formData.writing_score}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, writing_score: parseInt(e.target.value) }))
                }
              />
              <div className="score-badge">{formData.writing_score}</div>
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              'Running Model...'
            ) : (
              <>
                <Sparkles size={18} /> Predict Math Performance
              </>
            )}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: 16, color: '#ef4444', fontSize: '0.9rem' }}>
            Error: {error}
          </div>
        )}
      </div>

      {/* Result Section */}
      <div className="glass-card result-section">
        {result ? (
          <>
            <div>
              <h2 className="form-title">
                <Award size={22} color="#10b981" />
                Predicted Math Performance
              </h2>
              <div className="score-hero">
                <div className="score-circle">
                  <span className="score-value">{result.predicted_math_score}</span>
                  <span className="score-max">out of 100</span>
                </div>
                <div className={`grade-pill ${getGradeClass(result.grade)}`}>
                  Grade {result.grade}
                </div>
                <p className="performance-title">{result.performance_level}</p>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <p>Reading Score</p>
                  <h4>{result.reading_score}</h4>
                </div>
                <div className="metric-card">
                  <p>Writing Score</p>
                  <h4>{result.writing_score}</h4>
                </div>
                <div className="metric-card">
                  <p>Est. Percentile</p>
                  <h4>{result.percentile_estimate}%</h4>
                </div>
              </div>
            </div>

            <div className="recs-box">
              <h4>
                <Lightbulb size={18} color="#f59e0b" /> Key Recommendations & Insights
              </h4>
              <ul>
                {result.recommendations.map((rec, idx) => (
                  <li key={idx}>
                    <span className="bullet">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        ) : (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
              padding: 40,
              color: 'var(--text-muted)',
            }}
          >
            <Sparkles size={48} color="#6366f1" style={{ marginBottom: 16, opacity: 0.6 }} />
            <h3 style={{ color: 'var(--text-main)', marginBottom: 8 }}>Ready for Prediction</h3>
            <p style={{ fontSize: '0.9rem' }}>
              Select student attributes on the left and click "Predict Math Performance" to view the ML model output, grade estimate, and study recommendations.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
