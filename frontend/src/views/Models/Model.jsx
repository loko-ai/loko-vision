import { Box, HStack, Text, IconButton, Spacer, Stack, Tag, Button } from "@chakra-ui/react";
import { RiDeleteBin4Line } from "react-icons/ri";

export function Model({ name, onDelete, ...rest }) {
  return (
    <HStack
      bg="gray.200"
      borderRadius={"10px"}
      w="100%"
      py="0.5rem"
      px="1rem"
      {...rest}
    >
      <Stack spacing={0}>
        <HStack color={"#095789"}>
          <Box><Text as="b">{name}</Text></Box>
          {/* <Tag borderRadius={"10px"} p=".3rem" bg="pink.200" fontSize="xs">
            Not fitted
          </Tag> */}
        </HStack>
      </Stack>
      <Spacer />
      <HStack>
        <IconButton
          size="sm"
          borderRadius={"full"}
          bg='white'
          icon={<RiDeleteBin4Line />}
          onClick={(e) => {
            e.stopPropagation();
            e.preventDefault();
            onDelete(e);
          }}
        />
      </HStack>
    </HStack>
  );
}
