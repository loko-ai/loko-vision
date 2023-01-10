import {
    Button,
    IconButton,
    Stack,
    Tab,
    TabList,
    TabPanel,
    TabPanels,
    Tabs,
    Flex,
    Text
  } from "@chakra-ui/react";
  import { useContext } from "react";
  import { useCompositeState } from "ds4biz-core";
  import { CLIENT, StateContext } from "../../config/constants";
  import { RiArrowLeftLine, RiFontSize } from "react-icons/ri";
  import { useEffect, useState } from "react";
  import { CodeEditor } from '../../utils/CodeEditor';
  import * as React from 'react';
  



  
  export function TransformerDetails({ onClose, name }) {
    const state = useCompositeState({ blueprint: "Not Available" });

    const _state = useContext(StateContext);
    console.log("name::: ", {name})

    useEffect(() => {
        CLIENT.transformers[name]
        .get()
        .then((resp) => {state.blueprint=resp.data})
        .catch((err) => console.log(err));
      }, []);
    
    return (
      <Stack w="100%" h="100%" spacing="2rem" color='#A9A9A9'>
      <IconButton
            size="sm"
            w="30px"
            h="30px"
            borderRadius={"full"}
            bg='#222222'
            icon={<RiArrowLeftLine />}
            onClick={onClose}
          />
        <Flex w="100vw" h="100vh" p="2rem" color="#000000">
          <div class="container">
          <div class="item" style={{backgroundColor: '#f2eed9', width: '1000px',height: '50px'}}><Text as='b' fontSize='30px' color='#870f42'>Time Series Transformer: <Text as='i' fontSize='30px' color='#a91654'>{name}</Text></Text></div>
          <div class="item"><CodeEditor mode="json" readOnly value={JSON.stringify(state.blueprint, null, 2)} height="700px" />
          </div>
            </div>
        </Flex>

      </Stack>
    );
  }
  
//   {JSON.stringify(state.blueprint)}
  