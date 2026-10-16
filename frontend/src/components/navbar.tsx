import './navbar.css';

function Navbar() {
  return (
    <header className="navbar">
      <div className="nav-container">

        <div className="nav-brand-group">
          <div className="site-name">Sakshartha</div>

          <nav className="nav-links">
            <a href="/">Explore data</a>
            <a href="/">Solutions</a>
            <a href="/">Pricing</a>
          </nav>
        </div>

        <nav className="nav-actions">
          <a href="/">Login</a>
          <a href="/" className='signup-btn'>Sign up</a>
        </nav>

      </div>
    </header>
  );
}

export default Navbar;