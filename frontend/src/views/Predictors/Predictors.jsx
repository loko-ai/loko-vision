import { Button, Flex, HStack, Stack } from "@chakra-ui/react";
import { useCompositeState } from "ds4biz-core";
import React, { useState, useRef, useContext } from "react";
import { CLIENT, StateContext } from "../../config/constants";
import { Predictor } from "./Predictor";
import { PredictorCreation } from "./PredictorCreation";
import { Report } from "./Report";
import { RiAddFill,RiUploadCloud2Line,RiFileChartLine } from 'react-icons/ri';
import { PredictorDetails } from "./PredictorDetails";
import { saveAs } from 'file-saver';



export function Predictors({ predictors }) {
  const state = useCompositeState({ view: "list", name:null });
  const _state = useContext(StateContext);
  const ref_import = useRef();
  const ref_report = useRef();

  switch (state.view) {
    case "list":
      return (
        <Stack w="100%" h="100%" spacing="2rem">
          <HStack>
            <Button onClick={(e) => (state.view = "new")} leftIcon={<RiAddFill />}>New model</Button>
            <Button leftIcon={<RiUploadCloud2Line />}
                onClick={(e) => {
                    console.log('click');
                    ref_import.current.click()
                }}
            >
             Import
             </Button>
             <input
                type='file'
                accept=".zip"
                ref={ref_import}
                onChange={(e) => {
                    console.log('change import');
                    console.log(e.target.files[0]);
                    const formData = new FormData();
                    formData.append('file', e.target.files[0]);
                    CLIENT.models.import.post(formData).then(()=>location.reload()).catch((err) => console.log(err));
                }}
                onSubmit={(e) => {
                    e.preventDefault();
                    console.log('submit import');
                    _state.refresh = new Date();
                    // location.reload();
                }}
                style={{ display: 'none' }}/>
              <Button leftIcon={<RiFileChartLine />}
                onClick={(e) =>(
                ref_report.current.click()
                )}
              >
             Report
            </Button>
            <input
                type='file'
                accept=".eval"
                ref={ref_report}
                onChange={(e)=>{
                    const fileReader = new FileReader();
                    const { files } = event.target;
                    fileReader.readAsText(files[0], "UTF-8");
                    fileReader.onload = e => {
                      state.fname = files[0].name;
                      const content = e.target.result;
                      state.fdata = JSON.parse(content);
                    };
                    state.view = "report";
                    console.log('change report');
                }}
                onSubmit={(e)=>{
                    e.preventDefault();
                    console.log('submit report');
                }}
                style={{ display: 'none' }}/>
            
          </HStack>
          
          <Stack>
            {predictors.map((name) => (
              <Predictor
                onClick={(e) => {state.view = "show_blueprint", state.name ={name}}}
                name={name}
                key={name}
                onDelete={(e) =>
                  CLIENT.models[name].delete().then((resp) => {
                    _state.refresh = new Date();
                  })
                }
                onExport={(e) =>
                  CLIENT.models[name].export.get({responseType: "arraybuffer"})
                  .then(response => {
                    console.log('download');
                    console.log(response);
                    const blob = new Blob([response.data], {
                            type: 'application/octet-stream'
                            })
                    return blob
                    })
                    .then(blob => {
                    console.log(blob)
                    const filename = name+'.zip'
                    saveAs(blob, filename)
                    console.log('hello');
                    })
                  .catch(error => {
                    console.log(error);
                    })
                   }
              />
            ))}
          </Stack>
        </Stack>
      );
    case "new":
      return (
        
        <Flex w="100vw" h="100vh" p="2rem">
          <PredictorCreation onClose={(e) => (state.view = "list")} />
        </Flex>
      );
    case "show_blueprint":
      console.log("PREDICTORS in detailssssssss::::")
      return (
        <Flex w="100vw" h="100vh" p="2rem">
          <PredictorDetails onClose={(e) => (state.view = "list")} name={Object.values(state.name)} />
        </Flex>

      );
      case "report":
        return (
            <Report fname={state.fname} data={state.fdata} onClose={(e) => (state.view = "list")} />
        );
    
    default:
      break;
  }
}
