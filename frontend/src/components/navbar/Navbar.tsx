import {Link} from "react-router";

import './navbar.css';

function Navbar() {
  return (
    <header className="navbar">
      <div className="nav-container">

        <div className="nav-brand-group">
          <div className="site-name">Sakshartha</div>

          <nav className="nav-links">
            <Link to="/explore">Explore data</Link>
          </nav>
        </div>

        <nav className="nav-actions">
          <button type="button" className="login-btn" disabled>Login</button>
          <button type="button" className='signup-btn' disabled>Sign up</button>
        </nav>

      </div>
    </header>
  );
}

export default Navbar;