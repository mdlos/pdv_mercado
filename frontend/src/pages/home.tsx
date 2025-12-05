import { Box } from "@mui/material";
import { LayoutBase } from "../shared/layouts/LayoutBase";
import logo_mc from "../assets/logo_mc.svg";

const Home = () => {

  return (
    <LayoutBase titulo={""}>
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100%"
        width="100%"
      >
        <img
          src={logo_mc}
          alt="Logo"
          className="w-100 h-100 object-contain"
        // style={{
        //   maxWidth: "80%",
        //   maxHeight: "80%",
        //   objectFit: "contain",
        // }}
        />
      </Box>
    </LayoutBase>
  );
};

export default Home;