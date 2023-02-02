import {
    Flex,
    IconButton,
    Stack,
    HStack,
    VStack,
    Text,
    Thead,
    Tbody,
    Table,
    Tr,
    Td,
  } from "@chakra-ui/react";
  import { useContext } from "react";
  import { CLIENT, StateContext } from "../../config/constants";
  import { RiArrowLeftLine } from "react-icons/ri";
  import { Heatmap, Bar } from '../../plots';
  
  
  export function Report({ fname, data, onClose, ...rest }) {
    const _state = useContext(StateContext);
    const chartMargins = { top: 20, right: 10, bottom: 70, left: 20 };
    if (!data) return null;
    const cm = data.confusion_matrix;
    let labels = [];
    let orig_creport = data.metrics;
    console.log(data);
    console.log(cm);
    console.log(orig_creport);
    const acc = parseFloat(orig_creport['accuracy']).toFixed(3);
    let creport = Object.assign({}, orig_creport);
    delete creport['accuracy'];
    const creport_cols = [...["label"], ...Object.keys(creport[Object.keys(creport)[0]])];
    console.log(creport_cols);
    creport = Object.entries(creport).map((el, idx) => {
        let res = {};
        labels[idx] = el[0];
        const v = [...[el[0]], ...Object.entries(el[1]).map((el2,idx2) =>{
            let vv = el2[1];
            console.log(creport_cols[idx2+1]);
            if (creport_cols[idx2+1]!='support') {
                vv = parseFloat(vv).toFixed(3);
              }
            return vv})];
        v.map((vv, idx)=>{res[creport_cols[idx]]=vv});
        return(res)});
    console.log(creport);
    console.log(labels);
    const distro = data.true_dist.hist;
    console.log(distro);
    console.log(acc);
    const report_name = fname.slice(0,-5);
    var date = new Date(parseFloat(data.datetime)*1000);
    console.log(data.datetime);
    console.log(date.toLocaleString());
  
    return (
      <Stack w="100%" h="100%" spacing="1rem" color='#404040'>
      <IconButton
            align="left"
            size="sm"
            w="30px"
            h="30px"
            borderRadius={"full"}
            icon={<RiArrowLeftLine />}
            onClick={onClose}
          />
          <HStack w="100%" h="30vh" spacing="1rem">
              <Flex bg="#e2e8f0" color='white' borderRadius={"10px"} w="100%" h="100%">
                  <VStack w="100%" h="100%" spacing=".1rem">
                      <Text fontSize="lg" color='#1a202c' pl="1rem" pt="1rem" pb="1rem" w="100%"><b></b></Text>
                      <Text fontSize="18px" color='#1a202c' pl="1.5rem" pt=".2rem" w="100%" key="1"><b>name</b>: {report_name}</Text>
                      <Text fontSize="18px" color='#1a202c' pl="1.5rem" pt=".2rem" w="100%" key="1"><b>date</b>: {date.toLocaleString()}</Text>
                  </VStack>
              </Flex>
              <Flex bg="#e2e8f0" color='white' borderRadius={"10px"} w="100%" h="100%">
                  <VStack w="100%" h="100%" spacing=".1rem">
                      <Text fontSize="lg" color='#1a202c' pl="1rem" pt="1rem" w="100%"><b> Distribution </b></Text>
                      <Bar data={distro} />
                  </VStack>
              </Flex>
          </HStack>
          <HStack w="100%" h="40vh" spacing="1rem">
              <Flex bg="#e2e8f0" color='white' borderRadius={"10px"} w="100%" h="100%">
                  <VStack w="100%" h="100%" spacing=".1rem">
                      <Text fontSize="lg" color='#1a202c' pl="1rem" pt="1rem" w="100%"><b> Confusion matrix </b></Text>
                      <Heatmap data={cm} labels={labels} />
                  </VStack>
              </Flex>
  
              <Flex bg="#e2e8f0" color='white' borderRadius={"10px"} w="100%" h="100%">
                  <VStack w="100%" h="100%" spacing="2rem">
                      <Text fontSize="lg" color='#1a202c' pl="1rem" pt="1rem" w="100%"><b> Classification report </b></Text>
                      <Text fontSize="14px" color='#1a202c' pl="2rem" pt=".2rem" w="100%" key="1"><b>accuracy</b>: {acc}</Text>
                      <Table size="sm" color='#1a202c' w="90%" h="70%">
                          <Thead>
                              <Tr>
                                  {creport_cols.map((el, i) => (
                                      <Td borderColor="gray.600" fontSize={"12px"} key={i}>
                                      <b>
                                      {el}
                                      </b>
                                      </Td>))}
                              </Tr>
                          </Thead>
                          <Tbody>
                              {creport.map((row, i) => {
                                  return(
                                      <Tr key={i+1}>
                                      {Object.values(row).map((c, j) => (<Td borderColor="gray.600" fontSize={"12px"} key={i+j+5}>
                                                              {c}
                                                         </Td>))}
                                      </Tr>)})}
                          </Tbody>
                      </Table>
                  </VStack>
              </Flex>
          </HStack>
      </Stack>
    );
  }