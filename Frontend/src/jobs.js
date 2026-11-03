import axios from 'axios';
import Cookies from 'js-cookie';

const API = import.meta.env.VITE_API_URL;
const CHECK_EVERY = 3000;

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const waitForJob = async (response) => {
  let job = response.data;
  while (job.status === "running") {
    await wait(CHECK_EVERY);
    const next = await axios.get(`${API}/jobs/${job.job_id}`, { headers: { Authorization: `Bearer ${Cookies.get("token")}` } });
    job = next.data;
  }
  if (job.status === "failed") {
    throw { response: { status: 400, data: { detail: job.error } } };
  }
  return { data: job.result };
};
