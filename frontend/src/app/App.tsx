import { Route, Routes } from "react-router";
import Navbar from "../components/navbar/Navbar";
import HomePage from "../pages/HomePage";
import ExplorerDataPage from "../pages/ExplorerDataPage";
import IndicatorDetailPage from "../pages/IndicatorDetailPage";
function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/explore" element={<ExplorerDataPage/>} />
          <Route
    path="/indicators/:code"
    element={<IndicatorDetailPage />}
  />
      </Routes>

    </>
  )

}

export default App;