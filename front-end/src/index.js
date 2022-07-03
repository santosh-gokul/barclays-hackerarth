import React, { useState, useEffect} from "react";
import ReactDOM from "react-dom/client";

import "./styles.css";
import logoLeft from "./chevron-left-solid.svg"
import logoRight from "./chevron-right-solid.svg"
import plus from "./plus-solid.svg"
import minus from "./minus-solid.svg"
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, Popup  } from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import TextField from "@mui/material/TextField";
import jwt_decode from "jwt-decode";
import { ReactNotifications } from 'react-notifications-component'
import { Store } from 'react-notifications-component';
import 'react-notifications-component/dist/theme.css'


function App() {

  const baseEndpoint = "https://barclays-hackerearth.herokuapp.com";

  useEffect(() => {
    var currentTimeStamp = new Date();
    var seconds = currentTimeStamp.getTime() / 1000;
    console.log(isLoggedIn)
    if (sessionExpiry<=seconds){
      console.log(sessionExpiry)
      clearCache();
      if(sessionExpiry!=-1)
        Store.addNotification({
          title: 'Session Expired',
          message: 'Pls login again',
          type: 'warning',                        
          container: 'top-right',                
          animationIn: ["animated", "fadeIn"],     
          animationOut: ["animated", "fadeOut"],  
          dismiss: {
            duration: 3000 
          }
        })
    }
    if(!window.sessionStorage.getItem("coordinates")){
    navigator.geolocation.getCurrentPosition(function(position) {
      setCoordinates([position.coords.latitude, position.coords.longitude])
    });
  }
    
  }, []);

    function getSessionStorageOrDefault(key, defaultValue) {
      const stored = window.sessionStorage.getItem(key);
      
      if (!stored || stored==undefined) {
        return defaultValue;
      }
      return JSON.parse(stored);
    }

  // React States
  const [errorMessages, setErrorMessages] = useState("");
  const [isLoggedIn, setIsSubmitted] = useState(getSessionStorageOrDefault("isLoggedIn", false));
  const [itemCount, setCartCount] = useState(getSessionStorageOrDefault("itemCount", {}));
  const [menuItems, setMenuItems] = useState(getSessionStorageOrDefault("menuItems", []));
  const [menuItemPrice, setMenuItemPrice] = useState(getSessionStorageOrDefault("menuItemPrice", []));
  const [currentPage, setCurrentPage] = useState(getSessionStorageOrDefault("currentPage", 0));
  const [cartFilled, setCartFilled] = useState(getSessionStorageOrDefault("cartFilled", false));
  const [coordinates, setCoordinates] = useState(getSessionStorageOrDefault("coordinates", [0,0]));
  const [checkout, setCheckout] = useState(getSessionStorageOrDefault("checkout", false));
  const [userInfo, setUserInfo] = useState(getSessionStorageOrDefault("userInfo", {}));
  const [menuItemsTemp, setMenuItemsTemp] = useState(getSessionStorageOrDefault("menuItemsTemp", []));
  const [menuItemPriceTemp, setMenuItemsPriceTemp] = useState(getSessionStorageOrDefault("menuItemPriceTemp", []));
  const [sessionExpiry, setSessionExpiry] = useState(getSessionStorageOrDefault("sessionExpiry", -1))
  const [token, setToken] = useState(getSessionStorageOrDefault("token", ""))
  const [totalDiscount, setTotalDiscount] = useState(getSessionStorageOrDefault("totalDiscount", []))
  const [storeCoordinates, setStoreCoordinates] = useState(getSessionStorageOrDefault("storeStoreCoordinates", [0,0]));
  const [orderToken, setOrderToken] = useState(getSessionStorageOrDefault("orderToken", ""));
  const [storeName, setStoreName] = useState(getSessionStorageOrDefault("storeName", ""));
  const [storeDistance, setStoreDistance] = useState(getSessionStorageOrDefault("storeDistance", 0));

  useEffect(() => {
    window.sessionStorage.setItem("isLoggedIn", isLoggedIn);
    window.sessionStorage.setItem("itemCount", JSON.stringify(itemCount));
    window.sessionStorage.setItem("menuItems", JSON.stringify(menuItems));
    window.sessionStorage.setItem("menuItemPrice", JSON.stringify(menuItemPrice));
    window.sessionStorage.setItem("currentPage", currentPage);
    window.sessionStorage.setItem("cartFilled", cartFilled);
    window.sessionStorage.setItem("coordinates", JSON.stringify(coordinates));
    window.sessionStorage.setItem("storeCoordinates", JSON.stringify(storeCoordinates));
    window.sessionStorage.setItem("checkout", checkout);
    window.sessionStorage.setItem("userInfo", JSON.stringify(userInfo));
    window.sessionStorage.setItem("menuItemsTemp", JSON.stringify(menuItemsTemp));
    window.sessionStorage.setItem("menuItemPriceTemp", JSON.stringify(menuItemPriceTemp));
    window.sessionStorage.setItem("sessionExpiry", sessionExpiry);
    window.sessionStorage.setItem("token", JSON.stringify(token));
    window.sessionStorage.setItem("totalDiscount", JSON.stringify(totalDiscount));
    window.sessionStorage.setItem("orderToken", JSON.stringify(orderToken));
    window.sessionStorage.setItem("storeName", JSON.stringify(storeName));
    window.sessionStorage.setItem("storeDistance", JSON.stringify(storeDistance));



  }, [isLoggedIn, itemCount, menuItems, , menuItemPrice,
  currentPage, cartFilled, checkout, userInfo, menuItemsTemp, menuItemsTemp, coordinates, sessionExpiry,
token, totalDiscount, storeCoordinates, orderToken, storeDistance, storeName]);
  



  const clearCache = () => {
    setIsSubmitted(false);
    setCartCount({})
    setMenuItems([])
    setMenuItemPrice([])
    setCurrentPage(0);
    setCartFilled(false);
    setCoordinates([0,0]);
    setStoreCoordinates([0,0]);
    setCheckout(false);
    setUserInfo({});
    setMenuItemsTemp([]);
    setMenuItemsPriceTemp([]);
    setSessionExpiry(-1);
    setToken("");
    setTotalDiscount([]);
    setOrderToken("");
    setStoreName("");
    setStoreDistance(0);

    navigator.geolocation.getCurrentPosition(function(position) {
      setCoordinates([position.coords.latitude, position.coords.longitude])
    });
  }

  const incPage = () => {
    if ((currentPage+2)>Math.ceil(menuItems.length/4))
      return;
    setCurrentPage(currentPage+1);
  }

  const decPage = () => {
    if (currentPage-1<0)
      return;
    setCurrentPage(currentPage-1);
  }

  const finalizeCart = () => {
    let item_selected = 0;
    for (var key in itemCount){
      item_selected+=itemCount[key]
    }
    if(item_selected>0)
      setCartFilled(true);
    else{
      Store.addNotification({
        title: 'Empty cart',
        message: 'Pls add items to proceed',
        type: 'warning',                        
        container: 'top-right',                
        animationIn: ["animated", "fadeIn"],     
        animationOut: ["animated", "fadeOut"],  
        dismiss: {
          duration: 3000 
        }
      })
    }
  }

  const finalizeCheckout = () => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({'item_details': Object.entries(itemCount), 
      'user_location': {'lat': coordinates[0], 'lon': coordinates[1]}})
    };
    fetch(baseEndpoint+"/get_nearest_store_and_get_payment_token/"+token, requestOptions)
        .then(response => response.json())
        .then(data => {
            if(data.success){console.log("success", data.data.store_coordinates);
            setStoreCoordinates(data.data.store_coordinates);
            setOrderToken(data.order_token);
            setStoreName(data.data.store_name);
            setStoreDistance(data.distance);
            setCheckout(true);
          }});

  }

  const definalizeCart = () => {
    setCartFilled(false);
  }
  const handleLogin = (event) => {
    //Prevent page reload
    event.preventDefault();

    var { uname, pass } = document.forms[0];
    //Call the login API to validate the login call
    
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uname: uname.value, password: pass.value })
    };

    fetch(baseEndpoint+"/login", requestOptions)
        .then(response => response.json())
        .then(data => {
            if(data.success){
              var token = jwt_decode(data.token)
              setUserInfo({'userName': token.username});
              setSessionExpiry(token.expiry);
              setIsSubmitted(true);
              setToken(data.token);
              let menuItems_resp = []
              let menuItemPrices_resp = []
              let menuItemDiscounts_resp = []
              let cartCount_resp = {}
              const requestOptions_ = {
                method: 'GET',
                headers: { 'Content-Type': 'application/json'}
              };
              fetch(baseEndpoint+"/get_item_details/"+data.token, requestOptions_)
                .then(response => response.json())
                .then(data => {
                  console.log(data.success)
                  if(data.success){
                  data.data.forEach(element => {
                    cartCount_resp[element.name] = 0;
                    menuItems_resp.push(element.name);
                    menuItemPrices_resp.push(parseFloat(element.mrp));
                    menuItemDiscounts_resp.push(parseFloat(element.discountPercent));
                  });

                  setMenuItems(menuItems_resp);
                  setMenuItemPrice(menuItemPrices_resp);
                  setMenuItemsTemp(menuItems_resp);
                  setMenuItemsPriceTemp(menuItemPrices_resp);
                  console.log(JSON.stringify(cartCount_resp), "Hello");
                  setCartCount(cartCount_resp);
                  setTotalDiscount(menuItemDiscounts_resp);
                }
                else{
                  clearCache();
                  Store.addNotification({
                    title: 'Session Expired',
                    message: 'Pls login again',
                    type: 'warning',                        
                    container: 'top-right',                
                    animationIn: ["animated", "fadeIn"],     
                    animationOut: ["animated", "fadeOut"],  
                    dismiss: {
                      duration: 3000 
        }
      })
                }
              }
            );
            }
            else{
              Store.addNotification({
                title: 'Login',
                message: 'Pls check your login credentials',
                type: 'warning',                        
                container: 'top-right',                
                animationIn: ["animated", "fadeIn"],     
                animationOut: ["animated", "fadeOut"],  
                dismiss: {
                  duration: 3000 
                }
              })
            }
        });

    //Call the menu-api for item list and populate everything with 0.

    
  //   setCartCount({'Soap': 0, 'Powder': 0, 'Shampoo': 0, 'Juice': 0, 'Soap1': 0,
  // 'Juice1': 0, 'Shampoo1': 0, 'Powder1': 0});
    // setMenuItems(['Soap', 'Powder', 'Shampoo', 'Juice', 'Soap1', 'Juice1', 'Shampoo1', 'Powder1']);

    // setMenuItemPrice([100, 200, 300, 100, 200, 300, 40, 80]);

    // setMenuItemsTemp(['Soap', 'Powder', 'Shampoo', 'Juice', 'Soap1', 'Juice1', 'Shampoo1', 'Powder1']);
    // setMenuItemsPriceTemp([100, 200, 300, 100, 200, 300, 40, 80]);

  };

  const processIncrementAction = (item) => {
      let existingCount = itemCount[item];
      setCartCount({...itemCount, [item]: existingCount+1})
  };

  const processDecrementAction = (item) => {
      let existingCount = itemCount[item];
      setCartCount({...itemCount, [item]: Math.max(existingCount-1,0)})
  };
  const populateMenu = () => {
    let populatedItem = []
    for(var item = 0; item<Math.min(menuItems.length, 4); item++){
        let itemCtr = item+4*currentPage;
        let item_id = "row_"+itemCtr;
        let plus_id = "plus_"+itemCtr;
        let minus_id = "minus_"+itemCtr;
        let itemName = menuItems[item+4*currentPage];
        let itemPrice = menuItemPrice[item+4*currentPage]
        populatedItem.push(
        <div className="row_menu">
          <span id={item_id} style={{paddingLeft: '1.5vmin', paddingRight: '1.5vmin'}}>
            {itemName} - {itemPrice}Rs.
            </span>
          <span>
            <input type="image" className="icon" src={minus} id={minus_id} onClick={() => processDecrementAction(itemName)}/>
            <span style={{paddingLeft: '.5vmin', paddingRight: '.5vmin'}}>{itemCount[menuItems[item+4*currentPage]]}</span>
            <input type="image" className="icon" src={plus} id={plus_id} onClick={()=>processIncrementAction(itemName)}/>
          </span>
        </div>
        )
    }

    return populatedItem;
  }

  const queryItems = (value) => {
    let filteredMenu = menuItemsTemp.filter((it) =>{
      if(value.length==0){
        setMenuItemPrice(menuItemPriceTemp)
        setMenuItems(menuItemsTemp)
    }
      else{
        return it.toLowerCase().includes(value.toLowerCase());
      }
    })

    if(value.length>0){
    let filteredMenuPrice = []
    filteredMenu.forEach(element => {
      filteredMenuPrice.push(menuItemPriceTemp[menuItemsTemp.indexOf(element)])
    });
    setMenuItems(filteredMenu)
    setMenuItemPrice(filteredMenuPrice)
  }


  }

  const orderSummary = () => {
    let populatedItem = []
    let totalAmount = 0;
    let discountedPrice = 0;
    
    for(var item = 0; item<menuItems.length; item++){
      if (itemCount[menuItems[item]]>0){
        totalAmount+=(menuItemPrice[item]*itemCount[menuItems[item]]);
        discountedPrice+=(itemCount[menuItems[item]]*menuItemPrice[item] *(1-totalDiscount[item]/100))
        populatedItem.push(
        <div className="row_menu">
          <span style={{paddingLeft: '1.5vmin', paddingRight: '1.5vmin'}}>
          ✅ {menuItems[item]+" x"+itemCount[menuItems[item]]}
            </span>
        </div>
        )
    }
    }

    populatedItem.push(
      <div className="row_menu">
        <span style={{paddingLeft: '1.5vmin', paddingRight: '1.5vmin'}}>
        {"Your order value: "+ totalAmount + "Rs."}
          </span>
          <span style={{paddingLeft: '1.5vmin', paddingRight: '1.5vmin'}}>
        {"After discount(s): "+ discountedPrice + "Rs."}
          </span>
      </div>
      )

    return populatedItem;
  }

  // Generate JSX code for error message
  const renderErrorMessage = (name) =>
    name === errorMessages.name && (
      <div className="error">{errorMessages.message}</div>
    );

  // JSX code for login form
  const renderForm = (
    <div className="form">
      <form onSubmit={handleLogin}>
        <div className="input-container">
          <label>Username </label>
          <input type="text" name="uname" required />
          {renderErrorMessage("uname")}
        </div>
        <div className="input-container">
          <label>Password </label>
          <input type="password" name="pass" required />
          {renderErrorMessage("pass")}
        </div>
        <div className="button-container">
          <input type="submit" />
        </div>
      </form>
    </div>
  );

  const cartPageRender = (
    cartFilled ? (<div>
      <div className='cart-page-title'>Order Summary.</div>
      <div id="wrapper">
        <div id="row1">
        <div id="col2"> 
          <div id="menu">
              {orderSummary()}
              </div>
          </div>
        </div>
        <div id="row1" style={{paddingTop:'2vmin',  display: 'flex', gap: '10px'}} >
        <input type="button" className="btn btn-primary btn-sm" id="place-order" value="Go Back"
                onClick={()=>{definalizeCart()}}/>
                <input type="button" className="btn btn-primary btn-sm" id="place-order" value="Proceed"
                onClick={()=>{finalizeCheckout()}}/>
            </div>
        
      </div>
      <div id="logout" style={{paddingTop:'2vmin'}}>
                <input type="button" className="btn btn-danger btn-sm" id="place-order" value="Logout"
                onClick={()=>{clearCache()}}/>
            </div>
    </div>) :
    (
    <div>
      <div className='cart-page-title'> {"Hey "+userInfo['userName']+", What'cha buyin. today?"}
      </div>
      <div id="rowText">
          <TextField
          id="outlined-basic"
          variant="outlined"
          label="Search for items..."
          size="small"
          onChange= { s => queryItems(s.target.value)}
        /></div>
      <div id="wrapper">
        <div id="row1">
                  <div id="col1"> 
                      <div style={{paddingRight: '3vmin'}}> <input type="image" src={logoLeft}
                      className="icon" id="go-left"
                      onClick={()=>{decPage()}}/></div> 
                  </div>
                  <div id="col2"> 
                      <div id="menu">
                      {populateMenu()}
                    </div>
                  </div>
                  <div id="col3"> 
                      <div style={{paddingLeft: '3vmin'}}> <input type="image" src={logoRight} 
                      className="icon" id="go-right"
                      onClick={()=>{incPage()}}/></div> 
                  </div>

        </div>
        <div id="row1" style={{paddingTop:'2vmin'}}>
                <input type="button" className="btn btn-primary btn-sm" id="place-order" value="Proceed to Checkout"
                onClick={()=>{finalizeCart()}}/>
            </div>
      
      </div>
      <div id="logout" style={{paddingTop:'2vmin'}}>
                <input type="button" className="btn btn-danger btn-sm" id="place-order" value="Logout"
                onClick={()=>{clearCache()}}/>
            </div>
    </div>)
  
  )

  let marker = L.icon({
    iconUrl: plus,
    iconRetinaUrl: plus,
    iconAnchor: [5, 55],
    popupAnchor: [10, -44],
    iconSize: [25, 55],
  });

  const renderCheckout = (
    <div id="wrapper">
        <div id="col1">
        <div className='payment-page-title'>Proceed to Payment. 
        </div>
        <div className='payment-page-button' >
        <input type="button" className="btn btn-danger btn-sm" id="place-order" value="Click here for payment"
        onClick={()=>{window.open(orderToken)}}/>
        </div>

        <div className='payment-page-info'>Your order is coming from: {storeName} @ a distance: {storeDistance}Kms. 
        </div>
        </div>
        <div>
            <MapContainer center={coordinates} zoom={12} >
              <TileLayer
                attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={coordinates} icon={marker}>
                <Popup>
                  Your location.
                </Popup>
              </Marker>
              <Marker position={storeCoordinates} icon={marker}>
                <Popup>
                  Store location.
                </Popup>
              </Marker>
              </MapContainer>

        </div>
        <div id="logout" style={{paddingTop:'2vmin'}}>
                <input type="button" className="btn btn-danger btn-sm" id="place-order" value="Logout"
                onClick={()=>{clearCache()}}/>
        </div>
        
    </div>
    
  )

  return (
    <div> 
      <ReactNotifications />{
      checkout ? renderCheckout :
      (isLoggedIn ? 
      cartPageRender
                  :<div className="app">
                    <div className="login-form">
                      <div className="title">Sign In</div>
                      {renderForm}
                    </div>
                  </div>)
  }
  
  
  </div>
  );
}
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

