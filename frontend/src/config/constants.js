import React from "react";
import { URLObject } from "../hooks/urls";

const baseURL = import.meta.env.VITE_BASE_URL || "/";

const CLIENT = new URLObject(baseURL);
const StateContext = React.createContext();

export { StateContext, CLIENT, baseURL };
