import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Userpri from './components/Userpri'
import UserLayout from './components/UserLayout'
import GithubCallback from './pages/GithubCallback'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import RepoPage from './pages/RepoPage'
import Repos from './pages/Repos'
import Notifications from './pages/Notifications'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'

function App() {
  return (
    <div>
      <BrowserRouter>
      <Routes>
        <Route path='/' element={<GithubCallback/>}/>
        <Route path='/login' element={<Login/>}/>
        <Route path='/register' element={<Register/>}/>
        <Route path='/forgot-password' element={<ForgotPassword/>}/>
        <Route path='/reset-password' element={<ResetPassword/>}/>

        <Route element={<Userpri><UserLayout /></Userpri>}>
          <Route path='/dashboard' element={<Dashboard/>}/>
          <Route path='/repos' element={<Repos/>}/>
          <Route path='/repo/:owner/:name' element={<RepoPage/>}/>
          <Route path='/notifications' element={<Notifications/>}/>
        </Route>

        <Route path='*' element={<h1>No Such Router Exist</h1>} />
      </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App
