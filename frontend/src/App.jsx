import {
  Box,
  Button,
  Flex,
  HStack,
  Spacer,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from "@chakra-ui/react";
import { useCompositeState } from "ds4biz-core";
import { useEffect, useState } from "react";
import reactLogo from "./assets/react.svg";
import { CLIENT, StateContext } from "./config/constants";
import { Predictors } from "./views/Predictors/Predictors";

function App() {
  const state = useCompositeState({
    predictors: [],
    view: "list",
    refresh: null,
  });

  useEffect(() => {
    CLIENT.models
      .get({ params: { model_type: "custom" } })
      .then((resp) => (state.predictors = resp.data))
      .catch((err) => console.log(err));
  }, [state.refresh]);

  switch (state.view) {
    case "list":
      return (
        <StateContext.Provider value={state}>
          <Flex w="100vw" h="100vh">
            <Tabs w="80%" p="2rem">
              <TabList>
                <Tab>Models</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <Predictors predictors={state.predictors} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Flex>
        </StateContext.Provider>
      );

    case "model":
      console.log("state view === MODEL")
      return (
        <Flex w="100vw" h="100vh" p="2rem">
          <Box onClick={(e) => (state.view = "list")}>Details</Box> #blueprint
        </Flex>
      );
    case "model_creation":
      return (
        <Flex w="100vw" h="100vh" p="2rem">
          <ModelCreation onClose={(e) => (state.view = "list")} />
        </Flex>
      );
  }
}

export default App;
