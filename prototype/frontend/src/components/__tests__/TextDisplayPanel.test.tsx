import { render, screen, waitFor } from "@testing-library/react";
import TextDisplayPanel from "../TextDisplayPanel";
import * as api from "../../services/api";

jest.mock("../../services/api");

test("renders text from API when visible", async () => {
  (api.getDisplayText as jest.Mock).mockResolvedValue({ text: "hello world" });
  render(<TextDisplayPanel isVisible={true} onClose={() => {}} />);
  await waitFor(() => {
    expect(screen.getByText("hello world")).toBeInTheDocument();
  });
});
