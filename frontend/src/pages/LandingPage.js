import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LandingPage.css';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            IPC to BNS Legal Transition Made Simple
          </h1>
          <p className="hero-subtitle">
            AI-powered legal reasoning platform for analyzing the transition from
            Indian Penal Code (IPC) to Bhartiya Nyaya Sanhita (BNS)
          </p>
          <p className="hero-description">
            Navigate the complexities of India's new criminal law with confidence.
            Our intelligent system provides section-by-section analysis, case law research,
            and comprehensive legal memos—all powered by advanced RAG technology and
            curated landmark judgments.
          </p>
          <div className="hero-actions">
            <button className="btn-primary btn-large" onClick={() => navigate('/register')}>
              Start Free 14-Day Trial
            </button>
            <button className="btn-secondary btn-large" onClick={() => navigate('/pricing')}>
              View Pricing
            </button>
          </div>
          <p className="trial-note">
            Professional tier features • No credit card required • Cancel anytime
          </p>
        </div>
      </section>

      {/* Key Features */}
      <section className="features-section">
        <h2 className="section-title">What You Can Accomplish</h2>
        <p className="section-description">
          Comprehensive legal research and analysis tools designed for lawyers,
          researchers, and legal professionals
        </p>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">⚖️</div>
            <h3>IPC ↔ BNS Section Mapping</h3>
            <p>
              Instantly map any IPC section to its BNS equivalent with detailed
              explanations of substantive, procedural, and linguistic changes.
            </p>
            <ul className="feature-benefits">
              <li>Complete coverage of all IPC sections</li>
              <li>Identify doctrinal shifts and repealed provisions</li>
              <li>Track punishment modifications</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3>Case Law Research (RAG)</h3>
            <p>
              Semantic search over landmark Supreme Court judgments using
              state-of-the-art Retrieval Augmented Generation technology.
            </p>
            <ul className="feature-benefits">
              <li>Search by facts, legal principles, or issues</li>
              <li>Curated database of landmark cases</li>
              <li>Relevance-ranked results with citations</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h3>Legal Memo Generation</h3>
            <p>
              Generate comprehensive lawyer-style memoranda analyzing IPC-BNS
              transitions with validity warnings for precedents.
            </p>
            <ul className="feature-benefits">
              <li>Multi-section analysis in single memo</li>
              <li>Case law integration with ratio decidendi</li>
              <li>Actionable recommendations included</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚠️</div>
            <h3>Validity Warnings</h3>
            <p>
              Automated flagging of precedents that may require review under
              the new BNS framework.
            </p>
            <ul className="feature-benefits">
              <li>Assess continuing applicability of case law</li>
              <li>Identify substantive vs linguistic changes</li>
              <li>Risk assessment for litigation strategy</li>
            </ul>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <h2 className="section-title">How It Works</h2>
        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Sign Up</h3>
            <p>Create your account and start with a 14-day Professional trial—no credit card required.</p>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Analyze</h3>
            <p>Enter any IPC section number to instantly see its BNS mapping, doctrinal changes, and relevant case law.</p>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <h3>Research</h3>
            <p>Use semantic case search to find relevant precedents based on facts, legal principles, or issues.</p>
          </div>

          <div className="step-card">
            <div className="step-number">4</div>
            <h3>Generate</h3>
            <p>Create comprehensive legal memos with one click—complete with analysis, case citations, and recommendations.</p>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="use-cases">
        <h2 className="section-title">Who Benefits?</h2>
        <div className="use-cases-grid">
          <div className="use-case-card">
            <h3>👨‍⚖️ Practicing Lawyers</h3>
            <p>
              Draft accurate pleadings, anticipate doctrinal shifts, and advise clients
              confidently on the impact of BNS provisions.
            </p>
          </div>

          <div className="use-case-card">
            <h3>🔬 Legal Researchers</h3>
            <p>
              Conduct systematic comparative analysis of IPC vs BNS, identify trends,
              and publish data-driven insights.
            </p>
          </div>

          <div className="use-case-card">
            <h3>🎓 Law Students</h3>
            <p>
              Master the transition between legal frameworks, understand case law
              evolution, and excel in examinations.
            </p>
          </div>

          <div className="use-case-card">
            <h3>🏛️ Law Firms</h3>
            <p>
              Equip your entire team with enterprise access, ensure consistency across
              practice groups, and boost efficiency.
            </p>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="technology">
        <h2 className="section-title">Built on Advanced AI Technology</h2>
        <div className="tech-features">
          <div className="tech-item">
            <h4>🤖 RAG-Powered Search</h4>
            <p>Retrieval Augmented Generation for accurate case law research</p>
          </div>
          <div className="tech-item">
            <h4>🧠 Semantic Understanding</h4>
            <p>Vector embeddings for meaning-based search, not just keywords</p>
          </div>
          <div className="tech-item">
            <h4>📊 Structured Database</h4>
            <p>Comprehensive IPC↔BNS mappings with metadata and annotations</p>
          </div>
          <div className="tech-item">
            <h4>⚡ Real-Time Analysis</h4>
            <p>Instant results powered by optimized AI inference pipelines</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Navigate the IPC-BNS Transition?</h2>
          <p>Join hundreds of legal professionals using our platform</p>
          <div className="cta-actions">
            <button className="btn-primary btn-large" onClick={() => navigate('/register')}>
              Start Free Trial
            </button>
            <button className="btn-secondary btn-large" onClick={() => navigate('/pricing')}>
              See Plans & Pricing
            </button>
          </div>
          <p className="cta-note">
            ✓ 14-day Professional access • ✓ No credit card required • ✓ Instant activation
          </p>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="disclaimer-section">
        <p className="disclaimer-text">
          <strong>Disclaimer:</strong> This system provides automated legal analysis for research and
          educational purposes. While we strive for accuracy, the content should not be considered as
          legal advice. Always consult qualified legal professionals for case-specific guidance and verification.
        </p>
      </section>
    </div>
  );
}

export default LandingPage;
