import React, { Component } from 'react';
import ReactGA from 'react-ga';
import './App.css';
import RecommendTitles from './Components/RecommendTitles';
import Footer from './Components/Footer';

class App extends Component {

  handler(e) {
    e.preventDefault()
  }

  constructor(props){
    super(props);

    ReactGA.initialize('dsafdsf');
    ReactGA.pageview(window.location.pathname);
    this.handler = this.handler.bind(this)
  }


  render() {
    return (
      <div className="App">
        <div className="content">
        <RecommendTitles/>
        </div>
        <div className="footer">
        <Footer/>
        </div>
      </div>
    );
  }
}

export default App;
