import React, { Component } from "react";
import { bindAll } from "lodash";

class RecommendTitles extends Component {

  constructor() {
    super();
    this.state = {
      searchInput: "",
      foundTitles: [],
      selectedTitleId: "", 
      recommendedTitles: []
    };

    bindAll(
      this, 
      "searchTitles",
      "handleSearchChange",
      "handleTitleSelect",
      "recommendTitles",
      "keyPress"
    );
  }

  searchTitles(e) {

    let searchString = this.state.searchInput;

    fetch('https://wsf1w4y8hf.execute-api.ap-southeast-2.amazonaws.com/live?search='+searchString, {
      "headers": {},
      "referrer": "",
      "referrerPolicy": "no-referrer-when-downgrade",
      "body": null,
      "method": "GET",
      "mode": "cors",
      "credentials": "omit"
    })
    .then(results => {return results.json();})
    .then(data => {
      this.setState({ 
        foundTitles: JSON.parse(data.titles).slice(0, 20), 
        selectedTitleId: "",
        recommendedTitles: []
      });
      return {
        foundTitles: this.state.foundTitles,
        selectedTitleId: this.state.selectedTitleId,
        recommendedTitles: this.state.recommendedTitles
      };
    });
  }

  handleSearchChange(e) {
    this.setState({
      searchInput: e.target.value
    });
  }

  handleTitleSelect(e) {
    this.setState({
      selectedTitleId: e.target.id,
    });
    console.log("selected: ", e.target.id)
  }

  keyPress(e){
    if(e.keyCode === 13){
        console.log('value', e.target.value);
        this.searchTitles(e);
    }
  }

  recommendTitles(e) {

    let reftitleid = this.state.selectedTitleId;

    fetch('https://wsf1w4y8hf.execute-api.ap-southeast-2.amazonaws.com/live?recommendfortitle='+reftitleid, {
      "headers": {},
      "referrer": "",
      "referrerPolicy": "no-referrer-when-downgrade",
      "body": null,
      "method": "GET",
      "mode": "cors",
      "credentials": "omit"
    })
      .then(results => {
        return results.json();
      })
      .then(data => {
        this.setState({ recommendedTitles: JSON.parse(data.titles)});
        return {
          recommendedTitles: this.state.recommendedTitles
        };
      });
  }

  render() {
    
    let titleSelectHandler = this.handleTitleSelect
    let foundTitles = this.state.foundTitles
    let selectedTitleId = this.state.selectedTitleId
    let recommendedTitles = this.state.recommendedTitles

     let titlesElems = this.state.foundTitles.map(
       function(element, i){
         var titleId = element.titleid
         var title = element.title
         let imageurl = element.imageurl;
         //console.log("image url: ", imageurl);
        
        if (imageurl === null){
          imageurl = "placeholder.png"
        }

        return (
          <div 
            key={i}
            className={titleId === selectedTitleId ? "App-Button-Active" : "App-Button-Default"}>
            <label className="title-label">{title}</label>
            <input 
              className={titleId === selectedTitleId ? "App-Button-Active" : "App-Button-Default"}
              id={titleId} 
              type="image" 
              src={imageurl} 
              alt={title}
              value={title} 
              title={title}
              onClick={titleSelectHandler}
            />
            <br />
          </div>
        );
      }
    )

     let recommendationsElems = this.state.recommendedTitles.map(
       function(element, i){
         var titleId = element.titleid
         let imageurl = element.imageurl;
         //console.log("image url: ", imageurl);
        
        if (imageurl === null){
          imageurl = "placeholder.png"
        }

         console.log("titleid: ", {titleId}.titleId)
         var title = element.title
         var tooltip_text = element.title
         var url = "https://www.imdb.com/title/"+{titleId}.titleId
        return (
          <tr key={i}>
            <td>
              <a href={url} 
                title={tooltip_text}
                target="_blank"
                rel="noreferrer">
                <img 
                  src={imageurl} 
                  alt={title}
                  className="table-image-thumbnail"
                />
              </a>
            </td>
            <td>
              <a href={url} 
                title={tooltip_text}
                target="_blank"
                rel="noreferrer">
                {title}
              </a>
            </td>
          </tr>
        )
      }
    )
    
    return (
      <div id="recommend-titles">
          <label>Search for a movie:  </label>
          <input
            type="text"
            id="search"
            name="search"
            placeholder="Type Title Here"
            className="Search-Field"
            onChange={this.handleSearchChange}
            onKeyDown={this.keyPress}
          />
          <input
            id="SearchButton"
            type="button"
            value="Search"
            className="Search-Button"
            onClick={this.searchTitles}
          />
          <br />
          <label className={typeof foundTitles !== 'undefined' && foundTitles.length > 0 ? "nothidden" : "hidden"}>
            Select movie to recommend on!
          </label>
          <br />
          <br />
          <div className="container5">
            {titlesElems}
          </div>
          <div className={selectedTitleId === "" ? "hidden" : "nothidden"}>
            <input
              id="RecommendButton"
              type="button"
              value="Find Movies For Me!"
              className="Search-Button"
              onClick={this.recommendTitles}
            />
            <br />
            <br />
          </div>
          <div className={typeof recommendedTitles !== 'undefined' && recommendedTitles.length > 0 ? "nothidden" : "hidden"}>
            <label>Recommended Movies:</label>
            <br />
            <br />
            <div className="container2">
              <table className="paleYellowRows">
                {recommendationsElems}
              </table>
            </div>
            <br />
            <br />
          </div>
          <br />
          <br />
      </div>
    );
  }
}

export default RecommendTitles;
