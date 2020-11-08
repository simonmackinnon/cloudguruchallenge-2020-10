import React, { Component } from 'react';
import ReactGA from 'react-ga';
import './App.css';
import Header from './Components/Header';
import RecommendTitles from './Components/RecommendTitles';
import Footer from './Components/Footer';

class App extends Component {

  handler(e) {
    e.preventDefault()
  }

  constructor(props){
    super(props);

    ReactGA.initialize('G-GJ0RZ871V6');
    ReactGA.pageview(window.location.pathname);
    this.handler = this.handler.bind(this)
  }


  render() {
    return (
      <div className="App">
        <div className="content">
        <Header/>
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
