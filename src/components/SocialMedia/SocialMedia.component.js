import {SocialContainer, SocialIcons} from "./SocialMedia.styles";
import {AiFillGithub, AiFillLinkedin} from "react-icons/ai";
import {FaTelegramPlane} from "react-icons/fa";
import {CgMail} from "react-icons/cg";

export default function SocialMedia({inFooter}) {
  return (
    <SocialContainer inFooter={inFooter}>
      <SocialIcons
        href="https://github.com/humam-hossain"
        title="Visit my github profile"
        target="_blank"
        rel="noopener noreferrer">
        <AiFillGithub size="3rem"/>
      </SocialIcons>
      <SocialIcons
        href="https://www.linkedin.com/in/humam-hossain-7ab762230/"
        title="Contact me on LinkedIn"
        target="_blank"
        rel="noopener noreferrer">
        <AiFillLinkedin size="3rem"/>
      </SocialIcons>
      <SocialIcons
        href="https://t.me/humamhossain"
        title="Contact me on Telegram"
        target="_blank"
        rel="noopener noreferrer">
        <FaTelegramPlane size="3rem"/>
      </SocialIcons>
      <SocialIcons
        href="mailto://humam.hossain.e@gmail.com"
        title="Send directly an email"
        target="_blank"
        rel="noopener noreferrer">
        <CgMail size="3rem"/>
      </SocialIcons>
    </SocialContainer>
  )}