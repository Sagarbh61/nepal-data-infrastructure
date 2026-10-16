import './hero.css';

function Hero(){
  return(
    <section className="hero">
      <h1>Understand Nepal through data.</h1>
      <p className='hero-description'>Explore statistics and numbers behind Nepal's Economy.</p>

      <div className="hero-actions">
        <a href="/" className='explore'>Explore the data</a>
        <a href="/" className='about'>About the project</a>
      </div>
    </section>
  )

}

export default Hero;